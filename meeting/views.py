from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.models import User

from meeting.forms import MeetingForm
from meeting.models import Meeting

from . import models
import datetime
from itertools import chain, groupby

''' Pulls a list of the user's projects '''
def pull_projects(profile):
    projects = {
        models.Member.UserProjectRole.OWNER: [],
        models.Member.UserProjectRole.ACTIVE: [],
        models.Member.UserProjectRole.INVITED: []
    }
    
    if profile is not None:
        try:
            members = models.Member.objects.filter(user=profile)
            for member in members:
                projects[member.role].append(member.project)
        except:
            pass
        
    return projects

def pull_profile(user):
    if user.is_authenticated:
        try:
            profile = models.Profile.objects.get(user=user)
            if profile:
                return profile
        except:
            pass
        
    return None
    
''' Render the home page '''
def index(request):
    app_url = request.path
    return render(request, 'home.html', {'app_url': app_url})

''' Render the default projects page '''
def projects(request):
    if not request.user.is_authenticated:
            return redirect('LoginProcess')
    app_url = request.path
    projects = pull_projects(pull_profile(request.user))
    return render(request, 'projects/active_pane/no_selection.html', {'app_url': app_url, 'projects': projects})

class ProjectCreationProcess(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        # collect the information about the new project
        title = request.POST.get('title') if request.POST.get('title') else None
        description = request.POST.get('description') if request.POST.get('description') else None
        invitees = request.POST.get('invitees') if request.POST.get('invitees') else None
        user = request.user if request.user.is_authenticated else None
        
        if user is None:
            return redirect('LoginProcess')
            
        profile = models.Profile.objects.get(user=user)
        invitee_profiles = set()
        errors = dict()
        if title is None or not title.strip():
            errors['title'] = 'Cannot be empty'
        if description is None or not description.strip():
            errors['description'] = 'Cannot be empty'
        if user is None:
            errors['user'] = 'Cannot be empty'
        if invitees is None or not invitees.strip():
            errors['invited'] = 'Cannot be empty'
        else:
            invitee_usernames = filter(lambda username: username, map(lambda username: username.strip(), invitees.split(',')))
            
            seen_users = set()
            for invitee in invitee_usernames:
                if not invitee and 'invited' not in errors:
                    errors['invited'] = 'Usernames cannot be blank'
                elif not invitee and 'blank' not in errors['invited']:
                    errors['invited'] += '; usernames cannot be blank'
                elif invitee in seen_users and 'invited' not in errors:
                    errors['invited'] = 'Cannot have duplicate username'
                elif invitee in seen_users and 'duplicate' not in errors['invited']:
                    errors['invited'] += '; cannot have duplicate username'
                elif invitee not in seen_users:
                    seen_users.add(invitee)
                    
            for user in seen_users:
                try:
                    u = User.objects.get(username=user)
                    p = models.Profile.objects.get(user=u)
                    invitee_profiles.add(p)
                except User.DoesNotExist:
                    if 'invite' not in errors:
                        errors['invited'] = 'Cannot invite unregistered user'
                    else:
                        errors['invited'] += '; cannot invited unregistered user'
            
        is_no_errors = not bool(errors)
        
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        
        if is_no_errors:
            project = models.Project.objects.create(project_name=title, description=description)
            models.Member.objects.create(project=project, user=profile, role=models.Member.UserProjectRole.OWNER)
            for invitee in invitee_profiles:
                models.Member.objects.create(project=project, user=invitee, role=models.Member.UserProjectRole.INVITED)
            return redirect("/meeting/projects/" + str(project.pk))
            # return render(request, 'projects/active_pane/create_project.html', {'app_url': app_url, 'success': 'Successfully created project!', 'projects': projects})
        else:
            return render(request, 'projects/active_pane/create_project.html', {'app_url': app_url, 'errors': errors, 'projects': projects})
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        return render(request, 'projects/active_pane/create_project.html', {'app_url': app_url, 'projects': projects})
            
''' Render the "edit project" form '''
class ProjectModificationProcess(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        title = request.POST.get('title') if request.POST.get('title') else None
        description = request.POST.get('description') if request.POST.get('description') else None
        user = request.user if request.user.is_authenticated else None
        
        if user is None:
            return redirect('LoginProcess')
        
        errors = dict()
        if title is None or not title.strip():
            errors['title'] = 'Cannot be empty'
        if description is None or not description.strip():
            errors['description'] = 'Cannot be empty'
            
        is_no_errors = not bool(errors)
        
        project_key = kwargs['project_key']
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        project = None
        
        try:
            project = models.Project.objects.get(pk=project_key)
        except:
            pass
        
        if is_no_errors and project is not None:
            try:
                project.project_name = title
                project.description = description
                project.save()
            except:
                pass
            
            return redirect('../' + str(project_key))
        else:
            return render(request, 'projects/active_pane/edit_project.html', {'app_url': app_url, 'projects': projects, 'project': project, 'errors': errors})
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        project = None
        
        try:
            project_key = kwargs['project_key']
            project = models.Project.objects.get(pk=project_key)
        except:
            pass
        
        return render(request, 'projects/active_pane/edit_project.html', {'app_url': app_url, 'projects': projects, 'project': project})

class ProjectViewProcess(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        project_key = kwargs['project_key']
        project = models.Project.objects.get(pk=project_key)
        
        if request.POST.get('action') == 'remove':
            print("member -> yeet")
            try:
                user = models.User.objects.get(pk=request.POST.get('user'))
                profile = pull_profile(user)
                models.Member.objects.get(user=profile, project=project).delete()
            except Exception as e:
                print(e)
            
            return redirect("./" + str(project_key))
        elif request.POST.get('action') == 'invite':
            print("member -> yoink")
            try:
                user = models.User.objects.get(username=request.POST.get('user'))
                profile = pull_profile(user)
                models.Member.objects.create(project=project, user=profile, role=models.Member.UserProjectRole.INVITED)
            except Exception as e:
                print(e)
                
            return redirect("./" + str(project_key))
        elif request.POST.get('action') == 'accept':
            print("invite -> yoink")
            try:
                user = request.user if request.user.is_authenticated else None
                profile = pull_profile(user)
                models.Member.objects.filter(user=profile, project=project).update(role=models.Member.UserProjectRole.ACTIVE)
            except Exception as e:
                print(e)
                
            return redirect("./" + str(project_key))
        elif request.POST.get('action') == 'reject':
            print("invite -> yeet")
            try:
                user = request.user if request.user.is_authenticated else None
                profile = pull_profile(user)
                models.Member.objects.get(user=profile, project=project).delete()
            except:
                print(e)
                
        return redirect('../projects')
        
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        app_url = request.path
        profile = pull_profile(request.user)
        projects = pull_projects(profile)
        
        project = None
        team = []
        potential_yoinks = []
        meetings = [] # depends on Courtney
        role = -1
        
        try:
            project = models.Project.objects.get(pk=kwargs['project_key'])
            
            members = models.Member.objects.filter(project=project)
            for member in members:
                team.append(member)
                if member.user == profile:
                    role = member.role
                    
            profiles = models.Profile.objects.all()
            for p in profiles:
                exists = False
                for t in team:
                    if p.user.get_username() == t.user.user.get_username():
                        exists = True
                if not exists:
                    potential_yoinks.append(p.user.get_username())
                    
            mtgs = models.Meeting.objects.filter(project=project)
            for mtg in mtgs:
                meetings.append(mtg)
                
        except Exception as e:
            print(e)
            
        return render(request, 'projects/active_pane/view_project.html', {'app_url': app_url, 'projects': projects, 'project': project, 'team': team, 'meetings': meetings, 'role': role, 'potential_yoinks': potential_yoinks})

class LoginProcess(View):
    def post(self, request, *args, **kwargs):
        # collect the user's information to log them in
        username = request.POST.get('inputUsername') if request.POST.get('inputUsername') else None
        password = request.POST.get('inputPassword') if request.POST.get('inputPassword') else None
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        app_url = request.path
        return render(request, 'login.html', {'app_url': app_url, 'errors': True})
    
    def get(self, request, *args, **kwargs):
        app_url = request.path
        return render(request, 'login.html', {'app_url': app_url})

class RegisterProcess(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('inputUsername') if request.POST.get('inputUsername') else None
        password = request.POST.get('inputPassword') if request.POST.get('inputPassword') else None
        confirm_password = request.POST.get('inputConfirmPassword') if request.POST.get('inputConfirmPassword') else None
        display_name = request.POST.get('inputDisplayName') if request.POST.get('inputDisplayName') else None
        errors = dict()
        existing_user = User.objects.filter(username=username).count()
        username_duplicate = False if existing_user == 0 else True
        
        if username is None:
            errors['usernameEmpty'] = True
        if username_duplicate is True:
            errors['usernameDuplicate'] = True
        if password is None:
            errors['passwordEmpty'] = True
        if confirm_password is None:
            errors['confirmEmpty'] = True
        if display_name is None:
            errors['displayEmpty'] = True
        if password != confirm_password:
            errors['passwordMatch'] = True

        is_no_errors = not bool(errors)

        if is_no_errors:
            u = User.objects.create_user(username, email=None, password=password)
            u.save()
            new_user = User.objects.get(username=u)
            new_user.profile.display_name = display_name
            new_user.save()
            return redirect('LoginProcess')
        else:
            app_url = request.path
            return render(request, 'register.html', {'app_url': app_url, 'errors': errors })

    
    def get(self, request, *args, **kwargs):
        app_url = request.path
        return render(request, 'register.html', {'app_url': app_url})

'''
    get_meetings_by_user returns a list of ALL (distinct) meetings
    for ALL projects that the user is a member of.
'''
def get_meetings_by_user(user):
    profile = pull_profile(user)
    projects = pull_projects(profile)
    meetings = []
    
    members = models.Member.objects.filter(user=profile)
    
    for member in members:
        if member.role != models.Member.UserProjectRole.INVITED:
            for project in projects[member.role]:
                project_meetings = models.Meeting.objects.filter(project_id=project.id)
                meetings.append(project_meetings)

    all_meetings = list(chain(*meetings))
    unique_results = [next(rows) for (key, rows) in groupby(all_meetings, key=lambda obj: obj.id)]

    return unique_results

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
        avlb_count = models.TimeAvailability.objects.filter(meeting_id=meeting.id).count()
        avlb_meeting_list.append({'meeting': meeting, 'avlb_count': avlb_count})

    context = {
        'meeting_list': avlb_meeting_list,
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
            avlb_count = models.TimeAvailability.objects.filter(meeting_id=meeting.id).count()
            avlb_meeting_list.append({'meeting': meeting, 'avlb_count': avlb_count})

        app_url = request.path
        # time_slots = models.TimeAvailability.objects.filter(meeting=meeting_id)
        time_slots = models.TimeAvailability.objects.raw('select * from meeting_timeavailability where meeting_id = %s', [meeting_id])
        json_data = models.TimeAvailability.objects.all();

        time_slots_json = "["
        for datum in json_data:
            meeting = '"meeting":{"id":"' + str(datum.meeting.id) + '","description":"' + datum.meeting.description + '"}';
            time_slots_json += '{"id":"' + str(datum.id) + '","start_time":"' + str(datum.start_time) + '","end_time":"' + str(datum.end_time) + '",' + meeting + '},';
        if len(time_slots_json) > 1:
            time_slots_json = time_slots_json[:-1]
        time_slots_json += ']';
        
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(time_slots_json);

        context = {
            'active_meeting': active_meeting,
            'meeting_list': avlb_meeting_list,
            'app_url': app_url,
            'time_slots': time_slots,
            'time_slots_json': time_slots_json
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

        # meetingId = request.POST.get('meeting_id')
        meeting = models.Meeting.objects.get(id=meeting_id) if models.Meeting.objects.get(id=meeting_id) else None
        app_url = request.path

        context = {
            'meeting_list': [],
            'active_meeting': meeting,
            'app_url': app_url,
            'success': True,
            'errors': dict(),
            'time_slots': None,
            'time_slots_json': None
        }
        
        if start_time is None:
            context["success"] = False
            context["errors"]["start_time"] = True
        if end_time is None:
            context["success"] = False
            context["errors"]["end_time"] = True

        if context["success"]:
            models.TimeAvailability.objects.create(start_time=start_time,
                                                end_time=end_time,
                                                meeting=meeting,
                                                user=profile)

        meeting_list = get_meetings_by_user(user)
        avlb_meeting_list = []

        # Get avlb counts
        for meeting in meeting_list:
            avlb_count = models.TimeAvailability.objects.filter(meeting_id=meeting.id).count()
            avlb_meeting_list.append({'meeting': meeting, 'avlb_count': avlb_count})
            
        time_slots = models.TimeAvailability.objects.filter(meeting=meeting_id)
        
        json_data = models.TimeAvailability.objects.all();
        time_slots_json = "["
        for datum in json_data:
            meeting = '"meeting":{"id":"' + str(datum.meeting.id) + '","description":"' + datum.meeting.description + '"}';
            time_slots_json += '{"id":"' + str(datum.id) + '","start_time":"' + str(datum.start_time) + '","end_time":"' + str(datum.end_time) + '",' + meeting + '},';
        if len(time_slots_json) > 1:
            time_slots_json = time_slots_json[:-1]
        time_slots_json += ']';

        context['meeting_list'] = avlb_meeting_list
        context['time_slots'] = time_slots
        context['time_slots_json'] = time_slots_json

        return render(request, 'availability/meeting_availability.html', context)

class AvailabilityDelete(View):
    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None        
        
        if user is None:
            return redirect('LoginProcess')
        
        id = request.POST.get('id') if request.POST.get('id') else None
        slot = models.TimeAvailability.objects.get(id=id)
        slot.delete()

        meeting_id = kwargs.get('meeting_id') if kwargs.get('meeting_id') else None
        # meetingId = request.POST.get('meeting_id')
        meeting = models.Meeting.objects.get(id=meeting_id) if models.Meeting.objects.get(id=meeting_id) else None

        meeting_list = get_meetings_by_user(user)
        avlb_meeting_list = []

        # Get avlb counts
        for meeting in meeting_list:
            avlb_count = models.TimeAvailability.objects.filter(meeting_id=meeting.id).count()
            avlb_meeting_list.append({'meeting': meeting, 'avlb_count': avlb_count})
            
        active_meeting = meeting
        app_url = request.path
        time_slots = models.TimeAvailability.objects.filter(meeting=meeting_id)
        
        json_data = models.TimeAvailability.objects.all();
        time_slots_json = "["
        for datum in json_data:
            meeting = '"meeting":{"id":"' + str(datum.meeting.id) + '","description":"' + datum.meeting.description + '"}';
            time_slots_json += '{"id":"' + str(datum.id) + '","start_time":"' + str(datum.start_time) + '","end_time":"' + str(datum.end_time) + '",' + meeting + '},';
        if len(time_slots_json) > 1:
            time_slots_json = time_slots_json[:-1]
        time_slots_json += ']';

        context = {
            'meeting_list': avlb_meeting_list,
            'active_meeting': active_meeting,
            'app_url': app_url,
            'time_slots': time_slots,
            'time_slots_json': time_slots_json
        }

        return render(request, 'availability/meeting_availability.html', context)
# For testing purpose
class TestTimeSlot:
    def __init__(self, tStart, tEnd, count):
        self.tStart = tStart
        self.tEnd = tEnd
        self.count = count
        self.members = []

# For testing purpose
class TestUser:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.timeSlots = []
class Voting(View):

    MEETING_DURATION = 1
    refinedSlots = [] #Refined available time slots
    users = []
    teamMember = []

    #Check if the user exists in the given list
    def checkMember(self,members, name):
        for m in range(len(members)):
            if members[m] == name:
                return True
        return False

    #Check if the timeslot exists in the given list
    def checkSlot(self, timeslots, ts):
        for s in range(len(timeslots)):
            if timeslots[s].tStart == ts.tStart and timeslots[s].tEnd == ts.tEnd:
                return True
        return False
    
    #Check if the identical(contains same members) timeslot exists in the given list
    def isIdentical(self, timeslots, ts):
        for s in range(len(timeslots)):
            if timeslots[s].tStart == ts.tStart and timeslots[s].tEnd == ts.tEnd:
                if set(timeslots[s].members) == set(ts.members):
                    print('Identical!!!!!!!!!!!!!!!!')
                    return True
        return False

    #Generate permutation list
    def permutation(self, lst): 
  
        # If list is empty then there are no permutations 
        if len(lst) == 0: 
            return [] 
    
        # If there is only one element in list then, only 
        # one permuatation is possible 
        if len(lst) == 1: 
            return [lst] 
    
        # Find the permutations for list if there are 
        # more than 1 characters 
    
        l = [] # empty list that will store current permutation 
    
        # Iterate the input(list) and calculate the permutation 
        for i in range(len(lst)): 
            m = lst[i] 
    
            # Extract list[i] or m from the list.  remLst is 
            # remaining list 
            remLst = lst[:i] + lst[i+1:] 
    
            # Generating all permutations where m is first 
            # element 
            for p in self.permutation(remLst): 
                l.append([m] + p) 
        return l 
  
    #Refine Available Time Slots list
    def refineASL(self, availableTimeSlotsLst):
        print('Refine ASL')
        FATS = []
        for i in range(len(availableTimeSlotsLst)):
            availableTimeSlots = []
            # Initialize FATS
            if len(FATS) == 0:
                FATS.append(availableTimeSlotsLst[0][0])

            availableTimeSlots = availableTimeSlotsLst[i]
            print(' ')
            for j in range(len(availableTimeSlots)):
                flag = True

                for k in range(len(FATS)):
                    
                    #Same Time Slot
                    if FATS[k].tStart == availableTimeSlots[j].tStart and FATS[k].tEnd == availableTimeSlots[j].tEnd:
                        flag = False
                        a = FATS[k].members
                        b = availableTimeSlots[j].members
                        if set(a) == set(b):
                            print('')
                            print('   Already exists!!!!!!!!!!!!!!!')

                        else:
                            print(' ')
                            print('a: ' + str(FATS[k].tStart) + '-' + str(
                                FATS[k].tEnd) + ' : ',end='')
                            for l in range(len(FATS[k].members)):
                                print(str(FATS[k].members[l] + ' '), end='')
                            print(' ')
                            print('b: ' + str(availableTimeSlots[j].tStart) + '-' + str(
                                availableTimeSlots[j].tEnd) + ' : ', end='')
                            for l in range(len(availableTimeSlots[j].members)):
                                print(str(availableTimeSlots[j].members[l] + ' '), end='')
                            print(' ')
                            if set(a) - set(b) and not set(b) - set(a):
                                print('a - b')
                                print(set(a) - set(b))
                                print('Do nothing!')
                            elif set(b) - set(a) and not set(a) - set(b) and len(b) > len(a):
                                print('b - a')
                                print(set(b) - set(a))

                                if self.isIdentical(FATS,availableTimeSlots[j]):
                                    print('******isIdentical is true******')

                                else:
                                    print('******isIdentical is false******')
                                    FATS[k].members.clear()
                                    for l in range (len(b)):   
                                        if not self.checkMember(FATS[k].members, b[l]):
                                            FATS[k].members.append(b[l])

                            elif set(set(b) - set(a)) != set(set(b) - set(a)):
                                print('set(set(b) - set(a)) != set(set(b) - set(a))')
                            else:
                                print('Something wrong with your logic')


                if flag:
                    FATS.append(availableTimeSlots[j])
                    print('Slot appended to availableTimeSlot ')
        return FATS
                    
    #Generate available time slots list from permutation members list
    def generateASL(self,teamMember):
        print('Generate ASL')
        availableTimeSlotsLst = []
        permutationlst = self.permutation(teamMember)
        print(len(permutationlst))
        for p in range(len(permutationlst)):
            print(' ')
            for l in range(len(permutationlst[p])):
                u = permutationlst[p][l].name
                print( u + ' ', end = '')
            print(' ')
            g = self.generateMeeting(permutationlst[p])
            availableTimeSlotsLst.append(g)
        return availableTimeSlotsLst

    #Refine available time slots
    def refineSlots(self,timeslots):

        cloneSlots = []
        aq = []
        removedLst = []

        for i in range(len(timeslots)):
            cloneSlots.append(timeslots[i])
        
        for i in range(len(timeslots)):
            for j in range(len(cloneSlots)):
                print(' ')
                a = timeslots[i].members
                b = cloneSlots[j].members
                ts1 = timeslots[i]
                ts2 = cloneSlots[j]
                print('a: ' + str(ts1.tStart) + '-' + str(ts1.tEnd) + ' ', end = '')
                for k in range(len(a)):
                    print(a[k], end='')
                print(' ')
                print('b: ' + str(ts2.tStart) + '-' + str(ts2.tEnd) + ' ', end = '')
                for k in range(len(b)):
                    print(b[k], end='')
                print(' ')
                if set(a) == set(b):
                    print('a = b ')
                    if ts1.tStart > ts2.tEnd or ts2.tStart > ts1.tEnd:
                        print('no overlapping time')
                        print('Do nothing')


                    elif ts1.tStart == ts2.tStart and ts1.tEnd == ts2.tEnd:
                            print('Same time slot: Do nothing')

                    elif ts1.tStart < ts2.tStart and ts1.tEnd < ts2.tEnd:
                        if (ts1.tEnd - ts2.tStart) < self.MEETING_DURATION:
                            print('Case 1A: Meeting time is ' + str(ts1.tEnd -
                            ts2.tStart) + ': Not enough time for meeting')
                        else:
                            # Start time of B and end time of A is overlapping
                            print('Case 1B: Start time of B and end time of A is overlapping')
                            temp = TestTimeSlot(ts1.tStart, ts2.tEnd,0)
                            for k in range(len(b)):
                                temp.members.append(b[k])
                            if not not self.checkSlot(aq, temp):
                                
                                removedLst.append(ts1)
                                removedLst.append(ts2)
                                print(str(ts1.tStart) + '-' + str(ts1.tEnd) + ' removed')
                                # timeslots.remove(ts1)
                                aq.append(temp)
                                # timeslots.append(temp)
                                print(str(temp.tStart) + '-' + str(temp.tEnd) + ' appended')

                        
                    elif ts1.tStart > ts2.tStart and ts1.tEnd > ts2.tEnd:
                        if (ts2.tEnd - ts1.tStart) < self.MEETING_DURATION:
                            print('Case 2A: Meeting time is ' + str(ts2.tEnd -
                                    ts1.tStart) + ': Not enough time for meeting')
                        else:
                            # Start time of A and End time of B is overlapping
                            print('Case 2B: Start time of A and End time of B is overlapping')
                            temp = TestTimeSlot(ts2.tStart, ts1.tEnd,0)
                            for k in range(len(b)):
                                temp.members.append(b[k])
                            if not self.checkSlot(aq, temp):
                                removedLst.append(ts1)
                                removedLst.append(ts2)
                                print(str(ts1.tStart) + '-' + str(ts1.tEnd) + ' removed')
                                # timeslots.remove(ts1)
                                # timeslots.append(temp)
                                aq.append(temp)
                                print(str(temp.tStart) + '-' + str(temp.tEnd) + ' appended')


                    elif ts1.tStart >= ts2.tStart and ts1.tEnd <= ts2.tEnd:
                        # Start time of A and End time of A is overlapping
                        print('Case 3: Start time of A and End time of A is overlapping')
                        if not self.checkSlot(removedLst, ts2):
                            removedLst.append(ts1)
                            print(str(ts1.tStart) + '-' + str(ts1.tEnd) + ' removed')
                            # timeslots.remove(ts1)


                    elif ts1.tStart <= ts2.tStart and ts1.tEnd >= ts2.tEnd:
                        # Start time of B and End time of B is overlapping
                        print('Case 4: Start time of B and End time of B is overlapping')
                        print('Do nothing')
                    else:
                        print('Someting wrong')

                elif set(a) - set(b):
                    print('a - b ')
                    print(set(a) - set(b))
                    if ts1.tStart == ts2.tStart and ts1.tEnd == ts2.tEnd:
                        print('Same time slot')
                        print('Do nothing')
                    else:
                        print('Not same time slot')
                        print('Do nothing')



                elif set(b) - set(a):
                    print('b - a')
                    if ts1.tStart == ts2.tStart and ts1.tEnd == ts2.tEnd:
                        print('Same time slot')
                        if not self.checkSlot(removedLst, ts2):
                            removedLst.append(ts1)
                            print(str(ts1.tStart) + '-' + str(ts1.tEnd) + ' removed')
                            # timeslots.remove(ts1)
                            # timeslots.append(ts2)
                            aq.append(ts2)
                            print(str(ts2.tStart) + '-' + str(ts2.tEnd) + ' appended')



                    else:
                        print('Not same time slot')
                        print('Do nothing')

                else:
                    print('Not same time slot')
                    print('Do nothing')



                # li = len(timeslots) - 1
                # lj = len(availableTimeSlots) - 1
                # # print('j = ' + str(j) + ': len(timeslots) - 1 = ' + str(lj))
                # if li == i and lj == j:
        for a in range(len(aq)):
            timeslots.append(aq[a])
        aq.clear()

        for r in range(len(removedLst)):
            timeslots.remove(removedLst[r])
        removedLst.clear()

        for i in range(len(timeslots)):
    
            if len(timeslots[i].members) == 1:
                removedLst.append(timeslots[i])
        for i in range(len(removedLst)):
            timeslots.remove(removedLst[i])

        return timeslots

    #Generate available time slots
    def generateMeeting(self,teamMember):
        u = 0
        rq = []# remove queue
        aq = []# add queue 
        tempTimeSlots = []

        while u < len(teamMember):

            #Initialize members for own slots
            for s in range(len(teamMember[u].timeSlots)):
                if not self.checkMember(teamMember[u].timeSlots[s].members, teamMember[u].name):
                    teamMember[u].timeSlots[s].members.append(teamMember[u].name)
            
            # Add first members timeslots to available time slots 
            # for first iteration if availableTimeSlots is empty
            if len(tempTimeSlots) == 0:
                for s in range(len(teamMember[u].timeSlots)):
                    tempTimeSlots.append(teamMember[u].timeSlots[s])

            else:
                
                for i in range(len(tempTimeSlots)):
                    for j in range(len(teamMember[u].timeSlots)):

                        ts1 = tempTimeSlots[i]
                        ts2 = teamMember[u].timeSlots[j]

                        if not self.checkMember(tempTimeSlots[i].members, teamMember[u].name):
                            # Compare each time slot
                            if ts1.tStart > ts2.tEnd or ts2.tStart > ts1.tEnd:
                                # no overlapping time
                                if not self.checkSlot(aq, ts2):
                                    if not self.checkMember(ts2.members,teamMember[u].name):
                                        ts2.members.append(teamMember[u].name)
                                    aq.append(ts2)

                                if not self.checkSlot(aq, ts1):
                                    aq.append(ts1)

                                if j == 0: # To make sure to add to remove queue just once 
                                    rq.append(tempTimeSlots[i])

                            elif ts1.tStart == ts2.tStart and ts1.tEnd == ts2.tEnd:
                                # Case1: Same time slot

                                ts = TestTimeSlot(ts1.tStart, ts1.tEnd, 1)
                                for m in range(len(tempTimeSlots[i].members)):
                                    ts.members.append(
                                        tempTimeSlots[i].members[m])
                                if not self.checkMember(ts.members, teamMember[u].name):
                                    ts.members.append(teamMember[u].name)
                            
                                if j == 0:

                                    rq.append(tempTimeSlots[i])
                                    aq.append(ts)

                                else:
                                    aq.append(ts)

                            elif ts1.tStart < ts2.tStart and ts1.tEnd < ts2.tEnd:
                                if (ts1.tEnd - ts2.tStart) < self.MEETING_DURATION:
                                    # Case 2-1: Start time of B and end time of A is overlapping
                                    #           but not enough time for meeting
                                    if not self.checkSlot(aq, ts2):
                                        if not self.checkMember(ts2.members, teamMember[u].name):
                                            ts2.members.append(teamMember[u].name)
                                        aq.append(ts2)
                                    
                                    if not self.checkSlot(aq, ts1):
                                        aq.append(ts1)
                                       
                                    if j == 0:
                                        rq.append(tempTimeSlots[i])

                                else:
                                    # Case 2-2: Start time of B and end time of A is overlapping

                                    ts = TestTimeSlot(ts2.tStart, ts1.tEnd, 0)
                                    for m in range(len(tempTimeSlots[i].members)):
                                        ts.members.append(
                                            tempTimeSlots[i].members[m])
                                    if not self.checkMember(ts.members, teamMember[u].name):
                                        ts.members.append(teamMember[u].name)

                                    if j == 0:
                                        rq.append(tempTimeSlots[i])
                                        aq.append(ts)
                                    else:
                                        aq.append(ts)

                            elif ts1.tStart > ts2.tStart and ts1.tEnd > ts2.tEnd:
                                if (ts2.tEnd - ts1.tStart) < self.MEETING_DURATION:
                                    # Case 3-1: Start time of A and End time of B is overlapping
                                    #           but not enough time for meeting

                                    if not self.checkSlot(aq, ts2):
                                        if not self.checkMember(ts.members, teamMember[u].name):
                                            ts2.members.append(teamMember[u].name)
                                        aq.append(ts2)
                                        
                                    if not self.checkSlot(aq, ts1):
                                        aq.append(ts1)
                                       
                                    if j == 0:
                                        rq.append(tempTimeSlots[i])

                                else:
                                    # Case 3-2: Start time of A and End time of B is overlapping

                                    ts = TestTimeSlot(ts1.tStart, ts2.tEnd, 1)
                                    for m in range(len(tempTimeSlots[i].members)):
                                        ts.members.append(
                                            tempTimeSlots[i].members[m])
                                    if not self.checkMember(ts.members, teamMember[u].name):
                                        if not self.checkMember(ts.members, teamMember[u].name):
                                            ts.members.append(teamMember[u].name)
                                        
                                    if j == 0:

                                        rq.append(tempTimeSlots[i])
                                        aq.append(ts)

                                    else:
                                        aq.append(ts)

                            elif ts1.tStart >= ts2.tStart and ts1.tEnd <= ts2.tEnd:
                                # Case 4: Start time of A and End time of A is overlapping

                                ts = TestTimeSlot(ts1.tStart, ts1.tEnd, 1)
                                for m in range(len(tempTimeSlots[i].members)):
                                    ts.members.append(
                                        tempTimeSlots[i].members[m])
                                if not self.checkMember(ts.members, teamMember[u].name):
                                    ts.members.append(teamMember[u].name)
                                    
                                if j == 0:
                                    rq.append(tempTimeSlots[i])
                                    aq.append(ts)
                                else:
                                    aq.append(ts)

                            elif ts1.tStart <= ts2.tStart and ts1.tEnd >= ts2.tEnd:
                                # Case 5: Start time of B and End time of B is overlapping

                                ts = TestTimeSlot(ts2.tStart, ts2.tEnd, 1)
                                for m in range(len(tempTimeSlots[i].members)):
                                    ts.members.append(
                                        tempTimeSlots[i].members[m])
                                if not self.checkMember(ts.members, teamMember[u].name):
                                    ts.members.append(teamMember[u].name)
                                    
                                if j == 0:
                                    rq.append(tempTimeSlots[i])
                                    aq.append(ts)
                                else:
                                    aq.append(ts)
                            else:
                                print('Someting wrong')

                            #Check if it's end of nested loop
                            li = len(tempTimeSlots) - 1
                            lj = len(teamMember[u].timeSlots) - 1

                            # When nested loop ends remove all objects in rq from the available time slots
                            if len(rq) != 0 and li == i and lj == j:
                                for r in range(len(rq)):
                                    if self.checkSlot(tempTimeSlots, rq[r]):
                                        tempTimeSlots.remove(rq[r])
                                rq = []

                            # When nested loop ends add all objects in aq to the availabile time slots
                            if len(aq) != 0 and li == i and lj == j:
                                for a in range(len(aq)):
                                    tempTimeSlots.append(aq[a])

                                aq = []    

                    #--------------------- For loop for teamMember's timeslots  ----------------------

                #--------------------- For loop for available timeslots ------------------------                       

            u += 1

        #---------------------------- while loop for teamMember  -----------------------------

        return tempTimeSlots

    def post(self, request,):
        duplicateSlot = False
        duplicateName = False
        nameFound = False
        add_name = request.POST.get('Name')
        if add_name:
            if len(self.users) != 0:
                for name in self.users:
                    if  add_name != None:
                        if add_name == name:
                            duplicateName = True
                            print('Duplicate name')
                if not duplicateName and add_name != None:
                    self.users.append(request.POST.get('Name'))
            else:
                if add_name != None:
                    self.users.append(request.POST.get('Name'))
        t = TestTimeSlot(-1,-1,-1)
        u = TestUser(None, 0)

        startTime = request.POST.get('tStart') if request.POST.get('tStart') else None
        endTime = request.POST.get('tEnd') if request.POST.get('tEnd') else None

        t.tStart = int(startTime) if startTime else None
        t.tEnd = int(endTime) if endTime else None
        u.name = request.POST.get('user')

        if t.tStart != -1 and u.name != None:
            for user in self.teamMember:
                duplicateSlot = False
                if u.name == user.name:
                    for timeslot in user.timeSlots:
                        if timeslot.tStart == t.tStart and timeslot.tEnd == t.tEnd: 
                            duplicateSlot = True
                            print('Duplicate slot')
                    if not duplicateSlot:
                        user.timeSlots.append(t)
                        duplicateSlot = False
                    nameFound = True 
            if not nameFound:
                u.timeSlots.append(t)
                self.teamMember.append(u)

        value = request.POST.get('generate')
        if value == 'g':
            g = self.generateASL(self.teamMember)
            self.refinedSlots = self.refineSlots(self.refineASL(g))
            


        context = {
            'users':self.users,
            'teamMember':self.teamMember,
            'availableTimeSlots':self.refinedSlots,
        }
        return render(request, 'voting/index.html', context)
    
    def get(self, request):

        context = {
            'users':self.users,
        }
        return render(request, 'voting/index.html', context)

class MeetingView(View):
   template_name = 'create_meeting.html'

   def get(self, request, project_key):
       if not request.user.is_authenticated:
            return redirect('LoginProcess')

       form = MeetingForm()
       try:
           project = models.Project.objects.get(pk=project_key)
       except:
           pass    
       return render(request, self.template_name, {'form': form, 'project': project})

   def post(self, request, project_key):

        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.project = models.Project.objects.get(pk=project_key)
            meeting.save()

            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            location = form.cleaned_data['location']
            optional_members = form.cleaned_data['optional_members']
            description = form.cleaned_data['description']
            form = MeetingForm()
            return redirect('../../../projects')
        args = {'form': form, 'start_date': start_date, 'end_date': end_date, 'location': location, 'optional_members': optional_members, 'description': description}
        return render(request, self.template_name, args)         

class ProfilePage(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        logged_in_user = request.user
        username = logged_in_user.username
        display_name = logged_in_user.profile.display_name
        return render(request, 'profile_page.html', { 'username': username, 'displayName': display_name, 'is_no_errors': True, 'get_load': True })

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        username = request.POST.get('inputUsername') if request.POST.get('inputUsername') else None
        display_name = request.POST.get('inputDisplayName') if request.POST.get('inputDisplayName') else None
        errors = dict()

        if display_name is None:
            errors['displayNameEmpty'] = True
        elif display_name.isspace() is True:
            errors['displayNameEmpty'] = True

        if username is None:
            errors['usernameEmpty'] = True
        elif username.isspace() is True:
            errors['usernameEmpty'] = True

        existing_user = User.objects.filter(username=username).count()
        username_duplicate = False if existing_user == 0 else True
        
        if username_duplicate is True:
            found_user = User.objects.filter(username=username)[0]
            if found_user.username != request.user.username:
                errors['usernameDuplicate'] = True

        is_no_errors = not bool(errors)
        if is_no_errors:
            editing_user = User.objects.get(username=request.user.username)
            editing_user.username = username
            editing_user.profile.display_name = display_name
            editing_user.save()
        else:
            logged_in_user = request.user
            username = logged_in_user.username
            display_name = logged_in_user.profile.display_name
        return render(request, 'profile_page.html', {'username': username, 'displayName': display_name, 'errors': errors, 'is_no_errors': is_no_errors, 'get_load': False })
      
