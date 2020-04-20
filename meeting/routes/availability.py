from django.shortcuts import render, redirect
from django.views.generic import View
from meeting.views import get_meetings_by_user
from meeting.views import pull_profile
from django.http import HttpResponseRedirect
from django.contrib import messages

from .. import models

def availability(request):
    if not request.user.is_authenticated:
            return redirect('LoginProcess')
    
    user = request.user if request.user.is_authenticated else None
    
    if user is None:
        return redirect('LoginProcess')

    meeting_list = get_meetings_by_user(user)
    avlb_meeting_list = []
    
    # Get avlb counts
    for meeting in meeting_list:
        avlb_count = models.TimeAvailability.objects.filter(meeting_id = meeting.id, user_id = user.id).count()
        avlb_meeting_list.append({'meeting': meeting, 'avlb_count': avlb_count})

    context = {
        'meeting_list': avlb_meeting_list,
        'user': user
    }

    return render(request, 'availability/index.html', context)


class Availability(View):
    def get(self, request, meeting_id):
      
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        user = request.user if request.user.is_authenticated else None
        
        if user is None:
            return redirect('LoginProcess')

        meeting_list = get_meetings_by_user(user)
        active_meeting = [meeting for meeting in meeting_list if meeting.id == meeting_id][0]
        avlb_meeting_list = []

        # Get avlb counts
        for meeting in meeting_list:
            avlb_count = models.TimeAvailability.objects.filter(meeting_id = meeting.id, user_id = user.id).count()
            avlb_meeting_list.append({'meeting': meeting, 'avlb_count': avlb_count})

        app_url = request.path
        
        time_slots = get_timeslots(user.id, meeting_id)

        json_data = models.TimeAvailability.objects.all();

        time_slots_json = get_json_timeslots()
        
        other_timeslots = get_other_timeslots(user.id, meeting_id)

        for k, v in other_timeslots.items():
            print(k, v)

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(time_slots_json);

        context = {
            'active_meeting': active_meeting,
            'meeting_list': avlb_meeting_list,
            'app_url': app_url,
            'time_slots': time_slots,
            'time_slots_json': time_slots_json,
            'other_timeslots': other_timeslots,
            'user': user
        }
        
        return render(request, 'availability/meeting_availability.html', context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        user = request.user if request.user.is_authenticated else None        
        
        if user is None:
            return redirect('LoginProcess')

        profile = pull_profile(user)

        start_time = request.POST.get('start_time') if request.POST.get('start_time') else None
        end_time = request.POST.get('end_time') if request.POST.get('end_time') else None
        meeting_id = kwargs.get('meeting_id') if kwargs.get('meeting_id') else None

        meeting = models.Meeting.objects.get(id = meeting_id) if models.Meeting.objects.get(id = meeting_id) else None

        context = {
            'success': True,
            'errors': dict()
        }
        
        if start_time is None:
            context["success"] = False
            context["errors"]["start_time"] = True
        if end_time is None:
            context["success"] = False
            context["errors"]["end_time"] = True

        if context["success"]:
            models.TimeAvailability.objects.create(start_time = start_time,
                                                end_time = end_time,
                                                meeting = meeting,
                                                user = profile)

        # TODO: server side validation error response
        
        return HttpResponseRedirect(self.request.path_info)

class AvailabilityDelete(View):
    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None        
        
        if user is None:
            return redirect('LoginProcess')
        
        aid = request.POST.get('id') if request.POST.get('id') else None
        slot = models.TimeAvailability.objects.get(id=aid)
        slot.delete()

        meeting_id = kwargs.get('meeting_id') if kwargs.get('meeting_id') else ""
        
        return HttpResponseRedirect("../" + str(meeting_id))


###############################################################################################################
# Helper functions
###############################################################################################################

# Get current user's time slots for the meeting
def get_timeslots(user_id, meeting_id):
    # time_slots = models.TimeAvailability.objects.filter(meeting=meeting_id, user=user_id)
    time_slots = models.TimeAvailability.objects.raw('select * from meeting_timeavailability where meeting_id = %s and user_id = %s', [meeting_id, user_id])

    return time_slots
        
# Get other users' time slots for the meeting
def get_other_timeslots(user_id, meeting_id):
    users = models.Profile.objects.exclude(id=user_id)
    other_timeslots = {}
    for u in users:
        other_timeslots[u.display_name] = models.TimeAvailability.objects.filter(meeting = meeting_id, user = u.id)
    
    return other_timeslots

# Get all timeslots in JSON format
def get_json_timeslots():
    json_data = models.TimeAvailability.objects.all();
    time_slots_json = "["
    for datum in json_data:
        meeting = '"meeting":{"id":"' + str(datum.meeting.id) + '","description":"' + datum.meeting.description + '"}';
        time_slots_json += '{"id":"' + str(datum.id) + '","start_time":"' + str(datum.start_time) + '","end_time":"';
        time_slots_json += str(datum.end_time) + '",' + '"user_id":"' + str(datum.user.id) + '",' + meeting + '},';
    if len(time_slots_json) > 1:
        time_slots_json = time_slots_json[:-1]
    time_slots_json += ']';

    return time_slots_json
