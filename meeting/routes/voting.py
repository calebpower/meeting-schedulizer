from django.shortcuts import render
from django.views.generic import View


from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from .. import models


from meeting.models import Meeting
from meeting.models import MeetingTime
from meeting.models import Vote
from meeting.models import TimeAvailability
from meeting.models import MeetingTimeOption
from meeting.views import pull_profile
from meeting.views import get_meetings_by_user

import datetime
from datetime import datetime, timedelta
import random
import time



class Person:
    def __init__(self, name):
        self.name = name
        self.slots_submitted = False
        self.isUser = False
        self.timeSlots = []

class TempTimeSlot:
    def __init__(self, start_time, end_time):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.members = []
        self.vote_count = 0

@receiver(post_save, sender=TimeAvailability)
def availability_save_handler(sender, instance,**kwargs): 
        REVIEW = 3   
        print('TimeAvailability Save Handler')
        meeting_time_option = MeetingTimeOption.objects.filter(meeting=instance.meeting)
        meeting_time_option.delete()
        print('Time slots added')
        if instance.meeting.state == REVIEW:
            Meeting.objects.filter(id=instance.meeting.id).update(state=models.Meeting.VoteState.CLOSE)
        
@receiver(post_delete, sender=TimeAvailability)
def availability_delete_handler(sender, instance, **kwargs):    
        print('TimeAvailability Delete Handler')
        meeting_time_option = MeetingTimeOption.objects.filter(meeting=instance.meeting)
        meeting_time_option.delete()
        # Meeting.objects.filter(id=instance.meeting.id).update(state=models.Meeting.VoteState.CLOSE)

class Voting(View):

    MEETING_DURATION = 1 * 60 * 60 * 1000 # Assume 1 hour


    #Check if the user exists in the given list
    def checkMember(self,members, name):
        for m in range(len(members)):
            if members[m] == name:
                return True
        return False

    #Check if the timeslot exists in the given list
    def checkSlot(self, timeslots, ts):
        for s in range(len(timeslots)):
            if timeslots[s].start_time == ts.start_time and timeslots[s].end_time == ts.end_time:
                return True
        return False
    
    #Check if the identical(contains same start time, end time,and members) timeslot exists in the given list
    def isIdentical(self, timeslots, ts):
        for s in range(len(timeslots)):
            if timeslots[s].start_time == ts.start_time and timeslots[s].end_time == ts.end_time:
                if set(timeslots[s].members) == set(ts.members):
                    # print('Identical!!!!!!!!!!!!!!!!')
                    return True
        return False

    #Generate permutation list to compare every possible case
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
  
    #Refine meeting time slots list
    def refine_meeting_time_slots_lst(self, availableTimeSlotsLst):
        # print('Refine ASL')
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
                    if FATS[k].start_time == availableTimeSlots[j].start_time and FATS[k].end_time == availableTimeSlots[j].end_time:
                        flag = False
                        a = FATS[k].members
                        b = availableTimeSlots[j].members
                        if set(a) == set(b):
                            print('')
                            # print('   Already exists!!!!!!!!!!!!!!!')

                        else:
                            print(' ')
                            # print('a: ' + str(FATS[k].start_time) + '-' + str(
                            #     FATS[k].end_time) + ' : ',end='')
                            # for l in range(len(FATS[k].members)):
                            #     print(str(FATS[k].members[l] + ' '), end='')
                            # print(' ')
                            # print('b: ' + str(availableTimeSlots[j].start_time) + '-' + str(
                            #     availableTimeSlots[j].end_time) + ' : ', end='')
                            # for l in range(len(availableTimeSlots[j].members)):
                            #     print(str(availableTimeSlots[j].members[l] + ' '), end='')
                            # print(' ')
                            if set(a) - set(b) and not set(b) - set(a):
                                print('')
                                # print('a - b')
                                # print(set(a) - set(b))
                                # print('Do nothing!')
                            elif set(b) - set(a) and not set(a) - set(b) and len(b) > len(a):
                                print('')
                                # print('b - a')
                                # print(set(b) - set(a))

                                if self.isIdentical(FATS,availableTimeSlots[j]):
                                    print('')
                                    # print('******isIdentical is true******')

                                else:
                                    # print('******isIdentical is false******')
                                    FATS[k].members.clear()
                                    for l in range (len(b)):   
                                        if not self.checkMember(FATS[k].members, b[l]):
                                            FATS[k].members.append(b[l])

                            elif set(set(b) - set(a)) != set(set(b) - set(a)):
                                print('set(set(b) - set(a)) != set(set(b) - set(a))')
                            else:
                                print('Something wrong')


                if flag:
                    FATS.append(availableTimeSlots[j])
                    # print('Slot appended to availableTimeSlot ')
        return FATS
                    
    #Generate meeting time slots list from permutation members list
    def generate_meeting_time_slots_lst(self,teamMember):
        # print('Generate ASL')
        availableTimeSlotsLst = []
        permutationlst = self.permutation(teamMember)
        print(len(permutationlst))
        for p in range(len(permutationlst)):
            # print(' ')
            # for l in range(len(permutationlst[p])):
            #     u = permutationlst[p][l].name
            #     print( u + ' ', end = '')
            # print(' ')
            g = self.generate_available_time_slots(permutationlst[p])
            availableTimeSlotsLst.append(g)
            # print(len(g))
            for t in g:
                print(str(t.start_time) + (' - ') + str(t.end_time) + ' : ', end='')
                print('www')
                print(str(len(t.members)))
                for m in t.members:
                    print(m)
                print(' ')


        return availableTimeSlotsLst

    #Generate random voting option
    def generate_meeting_time_option(self,start, end):
        timeslots = []
        if abs(end -  start) >= self.MEETING_DURATION and abs(end -  start) < self.MEETING_DURATION*2:
            ds = self.roundup_time(start,end)
            rStart = self.datetime_to_milli(ds)
            rEnd = rStart + self.MEETING_DURATION
            de = self.milli_to_datetime(rEnd)
            timeslots.append(TempTimeSlot(ds, de))

        else:
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # Check if meeting time has more than 30 min + meeting duration
            # if true, generate meeting time option like 00:10, 00:20, 00:30 and so on
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            print('More than Meeting time * 2')
            print('Generate randome meeting time')

            dt = self.roundup_time(start,end)
            rStart = self.datetime_to_milli(dt)

            while True:
                print(self.milli_to_datetime(rStart))
                temp = TempTimeSlot(self.milli_to_datetime(rStart), self.milli_to_datetime(rStart+self.MEETING_DURATION))
                timeslots.append(temp)
                rStart = rStart + self.MEETING_DURATION
                if (end - rStart) < self.MEETING_DURATION:
                    break

        return timeslots

   #Refine meeting time slots
    def refine_meeting_time_slots(self,timeslots):

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
                # print('a: ' + str(ts1.start_time) + '-' + str(ts1.end_time) + ' ', end = '')
                # for k in range(len(a)):
                #     print(a[k], end='')
                # print(' ')
                # print('b: ' + str(ts2.start_time) + '-' + str(ts2.end_time) + ' ', end = '')
                # for k in range(len(b)):
                #     print(b[k], end='')
                # print(' ')
                if set(a) == set(b):
                    # print('a = b ')
                    if ts1.start_time > ts2.end_time or ts2.start_time > ts1.end_time:
                        # print('no overlapping time')
                        # print('Do nothing')
                        print('')

                    elif ts1.start_time == ts2.start_time and ts1.end_time == ts2.end_time:
                            # print('Same time slot: Do nothing')
                            print('')
                    elif ts1.start_time < ts2.start_time and ts1.end_time < ts2.end_time:
                        if (ts1.end_time - ts2.start_time) < self.MEETING_DURATION:
                            # print('Case 1A: Meeting time is ' + str(ts1.end_time -
                            # ts2.start_time) + ': Not enough time for meeting')
                            print('')
                        else:
                            # Start time of B and end time of A is overlapping
                            # print('Case 1B: Start time of B and end time of A is overlapping')
                            temp = TempTimeSlot(ts1.start_time, ts2.end_time)
                            for k in range(len(b)):
                                temp.members.append(b[k])
                            if not not self.checkSlot(aq, temp):
                                
                                removedLst.append(ts1)
                                removedLst.append(ts2)
                                # print(str(ts1.start_time) + '-' + str(ts1.end_time) + ' removed')
                                aq.append(temp)
                                # print(str(temp.start_time) + '-' + str(temp.end_time) + ' appended')

                        
                    elif ts1.start_time > ts2.start_time and ts1.end_time > ts2.end_time:
                        if (ts2.end_time - ts1.start_time) < self.MEETING_DURATION:
                            # print('Case 2A: Meeting time is ' + str(ts2.end_time -
                            #         ts1.start_time) + ': Not enough time for meeting')
                            print('')
                        else:
                            # Start time of A and End time of B is overlapping
                            # print('Case 2B: Start time of A and End time of B is overlapping')
                            temp = TempTimeSlot(ts2.start_time, ts1.end_time)
                            for k in range(len(b)):
                                temp.members.append(b[k])
                            if not self.checkSlot(aq, temp):
                                removedLst.append(ts1)
                                removedLst.append(ts2)
                                # print(str(ts1.start_time) + '-' + str(ts1.end_time) + ' removed')
                                aq.append(temp)
                                # print(str(temp.start_time) + '-' + str(temp.end_time) + ' appended')


                    elif ts1.start_time >= ts2.start_time and ts1.end_time <= ts2.end_time:
                        # Start time of A and End time of A is overlapping
                        # print('Case 3: Start time of A and End time of A is overlapping')
                        if not self.checkSlot(removedLst, ts2):
                            removedLst.append(ts1)
                            # print(str(ts1.start_time) + '-' + str(ts1.end_time) + ' removed')
                            


                    elif ts1.start_time <= ts2.start_time and ts1.end_time >= ts2.end_time:
                        # Start time of B and End time of B is overlapping
                        # print('Case 4: Start time of B and End time of B is overlapping')
                        # print('Do nothing')
                        print('')
                    else:
                        print('Someting wrong')

                elif set(a) - set(b):
                    # print('a - b ')
                    # print(set(a) - set(b))
                    if ts1.start_time == ts2.start_time and ts1.end_time == ts2.end_time:
                        # print('Same time slot')
                        # print('Do nothing')
                        print('')
                    else:
                        # print('Not same time slot')
                        # print('Do nothing')
                        print('')



                elif set(b) - set(a):
                    # print('b - a')
                    if ts1.start_time == ts2.start_time and ts1.end_time == ts2.end_time:
                        # print('Same time slot')
                        if not self.checkSlot(removedLst, ts2):
                            removedLst.append(ts1)
                            # print(str(ts1.start_time) + '-' + str(ts1.end_time) + ' removed')
                            aq.append(ts2)
                            # print(str(ts2.start_time) + '-' + str(ts2.end_time) + ' appended')



                    else:
                        # print('Not same time slot')
                        # print('Do nothing')
                        print('')

                else:
                    # print('Not same time slot')
                    # print('Do nothing')
                    print('')

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

        print('Done')
        return timeslots
 
    #Generate time slots that all members available
    def generate_available_time_slots(self,teamMember):
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
                            if ts1.start_time > ts2.end_time or ts2.start_time > ts1.end_time:
                                # no overlapping time
                                if not self.checkSlot(aq, ts2):
                                    if not self.checkMember(ts2.members,teamMember[u].name):
                                        ts2.members.append(teamMember[u].name)
                                    aq.append(ts2)

                                if not self.checkSlot(aq, ts1):
                                    aq.append(ts1)

                                if j == 0: # To make sure to add to remove queue just once 
                                    rq.append(tempTimeSlots[i])

                            elif ts1.start_time == ts2.start_time and ts1.end_time == ts2.end_time:
                                # Case1: Same time slot

                                ts = TempTimeSlot(ts1.start_time, ts1.end_time)
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

                            elif ts1.start_time < ts2.start_time and ts1.end_time < ts2.end_time:
                                if (ts1.end_time - ts2.start_time) < self.MEETING_DURATION:
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

                                    ts = TempTimeSlot(ts2.start_time, ts1.end_time)
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

                            elif ts1.start_time > ts2.start_time and ts1.end_time > ts2.end_time:
                                if (ts2.end_time - ts1.start_time) < self.MEETING_DURATION:
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

                                    ts = TempTimeSlot(ts1.start_time, ts2.end_time)
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

                            elif ts1.start_time >= ts2.start_time and ts1.end_time <= ts2.end_time:
                                # Case 4: Start time of A and End time of A is overlapping

                                ts = TempTimeSlot(ts1.start_time, ts1.end_time)
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

                            elif ts1.start_time <= ts2.start_time and ts1.end_time >= ts2.end_time:
                                # Case 5: Start time of B and End time of B is overlapping

                                ts = TempTimeSlot(ts2.start_time, ts2.end_time)
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
                                print('Someting went wrong')

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

    #Find time slots that all members can attend
    def find_meeting_slots(self, timeslots, team):
        meeting_slots = []
        for slot in timeslots:
            if len(slot.members) == len(team):
                meeting_slots.append(slot)

        return meeting_slots

    #Convert deltatime to milliseconds
    def datetime_to_milli(self, dt):
        t = int(round(dt.timestamp() * 1000))
        return t
    
    #Convert milliseconds to deltatime
    def milli_to_datetime(self,milli):
        t = datetime.fromtimestamp(milli/1000)
        return t

    #Round up to the nearest time according to delta value
    def ceil_dt(self, dt, delta):
        return dt + (datetime.min - dt) % delta
    
    #Round up time
    def roundup_time(self,start,end):

        d1 = datetime.fromtimestamp(start/1000)
        #Round up to the nearest 30 min
        if end - start >= 30 * 60 * 1000 + self.MEETING_DURATION :
            print('Round up to the nearest 00 or 30 min')
            dt = self.ceil_dt(d1, timedelta(minutes=30))
            print(dt)
            return dt
        
        #Round up to the nearest 10 min
        elif end - start >= 10 * 60 * 1000 + self.MEETING_DURATION:
            print('Round up to the nearest 10 min')
            dt = self.ceil_dt(d1, timedelta(minutes=10))
            print(dt)
            return dt

        #Round up under 5 min
        elif end - start >= 5 * 60 * 1000 + self.MEETING_DURATION:
            if (d1.minute)%10 >= 5:
                print('>= 6 Round up to the nearest 10 min')
                dt = self.ceil_dt(d1, timedelta(minutes=10))
                print(dt)
                return dt
            else:
                print('Round up to the nearest 5 min')
                dt = self.ceil_dt(d1, timedelta(minutes=5))
                print(dt)
                return dt
        
        elif end - start == 4 * 60 * 1000 + self.MEETING_DURATION and (d1.minute)%10 != 0 and (d1.minute)%10 != 5:
            print('Round up to the nearest 5 min')
            dt = self.ceil_dt(d1, timedelta(minutes=5))
            print(dt)
            return dt

        elif end - start == 3 * 60 * 1000 + self.MEETING_DURATION and (d1.minute)%10 != 1 and (d1.minute)%10 != 6:
            print('Round up to the nearest 5 min')
            dt = self.ceil_dt(d1, timedelta(minutes=5))
            print(dt)
            return dt

        elif end - start == 2 * 60 * 1000 + self.MEETING_DURATION and (d1.minute)%10 != 1 and (d1.minute)%10 != 2 and (d1.minute)%10 != 6 and (d1.minute)%10 != 7 :
            print('Round up to the nearest 5 min')
            dt = self.ceil_dt(d1, timedelta(minutes=5))
            print(dt)
            return dt

        elif end - start == 1 * 60 * 1000 + self.MEETING_DURATION and (d1.minute)%10 != 1 and (d1.minute)%10 != 2 and (d1.minute)%10 != 3 and (d1.minute)%10 != 6 and (d1.minute)%10 != 7 and (d1.minute)%10 != 8:
            print('Round up to the nearest 5 min')
            dt = self.ceil_dt(d1, timedelta(minutes=5))
            print(dt)
            return dt
        else:
            print('No round-up')
            return d1


    def get(self, request, meeting_id, *args, **kwargs):
  
        team = []
        teamTest = []#For Debug
        meeting_time_slots = []
        meeting_time_options = []
        voted_slot = []
        votes = []
        fifty_fifty_votes = []
        project = None
        profile = None    
        
        state_ready = True # if user can vote
        state_review = False # if user can edit their available time slots
        state_closed = False # if vote session is over
        state_no_vote = False #no vote is needed

        CLOSE = 0
        OPEN = 1
        DONE = 2 
        REVIEW = 3
        REVOTE = 4
        NO_VOTE = 5

#****************************Initilize values************************************

        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        user = request.user if request.user.is_authenticated else None
        
        if user is None:
            return redirect('LoginProcess')
    

        meeting_list = get_meetings_by_user(user)
        active_meeting = [meeting for meeting in meeting_list if meeting.id == meeting_id][0]
        avlb_meeting_list = []
        for meeting in meeting_list:
            avlb_count = models.TimeAvailability.objects.filter(meeting_id=meeting.id).count()
            avlb_meeting_list.append({'meeting': meeting, 'avlb_count': avlb_count})

        app_url = request.path
        profile = pull_profile(user)
        time_slots = models.TimeAvailability.objects.filter(user=profile,meeting_id=meeting_id)
        json_data = models.TimeAvailability.objects.all()
        time_slots_json = "["
        for datum in json_data:
            meeting = '"meeting":{"id":"' + str(datum.meeting.id) + '","description":"' + datum.meeting.description + '"}'
            time_slots_json += '{"id":"' + str(datum.id) + '","start_time":"' + str(datum.start_time) + '","end_time":"' + str(datum.end_time) + '",' + meeting + '},'
        if len(time_slots_json) > 1:
            time_slots_json = time_slots_json[:-1]
        time_slots_json += ']'

        project = [meeting for meeting in meeting_list if meeting.id == meeting_id][0].project     
        members = models.Member.objects.filter(project=project)
        meeting = models.Meeting.objects.get(id=meeting_id) if models.Meeting.objects.get(id=meeting_id) else None
        ops = models.MeetingTimeOption.objects.filter(meeting_id=meeting_id)
        print('meeting_time_options length is '+ str(len(meeting_time_options)))
        for op in ops:
            meeting_time_options.append(op)

        votes = models.Vote.objects.filter(meeting_id=meeting_id)
        print('Number of votes: ' + str(len(votes)))
        print('Member length = ' + str(len(members)))
        for member in members:
            timeslots = models.TimeAvailability.objects.filter(user=member.user,meeting_id=meeting_id)
            print('username: ' + str(member.user.user.username))
            u = Person(member.user.user.username)
            uTest = Person(member.user.user.username) #For Debug
            if member.user.id == profile.user.id:
                u.isUser = True
                uTest.isUser = True #For Debug
            print('Timeslots length: ' + str(len(timeslots)))
            if timeslots:
                u.slots_submitted = True
                uTest.slots_submitted = True  #For Debug                
                for slot in timeslots:
                    print(str(slot.start_time) + '----' + str(slot.end_time))
                    #Convert to milli
                    start = self.datetime_to_milli(slot.start_time)
                    end = self.datetime_to_milli(slot.end_time)
                    t = TempTimeSlot(start, end)
                    t.members.append(member.user.user.username)
                    u.timeSlots.append(t)
                    tTest = TempTimeSlot(slot.start_time, slot.end_time) #For Debug
                    uTest.timeSlots.append(tTest) #For Debug
            
            else:
                state_ready = False
                Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.CLOSE)

            team.append(u)
            teamTest.append(uTest)

            for t in teamTest:
                print('name: ' + t.name)
                for s in t.timeSlots:
                    print(str(s.start_time) + '-'+ str(s.end_time))

        try:  
            
            if not meeting_time_options and state_ready:
                print('Generate Meeting Time Option')
                print(len(meeting_time_options))
                g_asl = self.generate_meeting_time_slots_lst(team)
                print('g_asl done')
                print(len(g_asl))
                r_slots = self.refine_meeting_time_slots(self.refine_meeting_time_slots_lst(g_asl))
                print('r_slots done')
                print(len(r_slots))
                meeting_time_slots = self.find_meeting_slots(r_slots, team)
                print('meeing_time_slots len = ' + str(len(meeting_time_slots)))
                
                for timeslot in meeting_time_slots:

                    start = timeslot.start_time
                    end = timeslot.end_time
                    dStart = self.milli_to_datetime(start)
                    dEnd = self.milli_to_datetime(end)
                    print(' ')
                    print('Before round-up')
                    print(dStart)

                    for option in self.generate_meeting_time_option(start, end):
                        meeting_time_options.append(option)
                print(len(meeting_time_options))

                #Save options to Database
                for i in range(len(meeting_time_options)):
                    meeting_time_option = MeetingTimeOption(start_time=meeting_time_options[i].start_time,
                                                    end_time=meeting_time_options[i].end_time,
                                                    meeting=meeting)
                    meeting_time_option.save()
                    meeting_time_options[i].id = meeting_time_option.id
    
                #Check status of meeting time option
                if len(meeting_time_options) == 0:
                    print('No meeting time option is generated and Vote Closed')
                    print('State changed')
                    Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.REVIEW)
                    state_review = True

                elif len(meeting_time_options) == 1:
                    state_no_vote = True
                    print('No vote needed')
                    MeetingTime.objects.filter(meeting=meeting).delete()
                    print('State changed')
                    Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.NO_VOTE)
                    meeting_time = MeetingTime(start_time=meeting_time_options[i].start_time,
                                                    end_time=meeting_time_options[i].end_time,
                                                    meeting=meeting)
                    meeting_time.save()
                else:
                    print('Meeting time options are generated and ready to vote')
                    Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.OPEN)

            else:
                if voted_slot:
                    print('You voted')

        except Exception as e:
            print(e)
            print(' ')

    #*******************************Check vote state***************************************

        print('START Meeting Current State is ' + str(meeting.state))


        if meeting.state == DONE:
            print('Vote Closed')
            state_closed = True
            # For Debugging
            # Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.CLOSE)


        elif meeting.state == NO_VOTE or len(ops) == 1:
            print('No vote needed!!')
            state_no_vote = True
            # Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.CLOSE)
            

        elif meeting.state == REVIEW:
            print('Review required')
            state_review = True
            # Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.CLOSE)

        elif meeting.state == OPEN:
            
            print('Vote is Open')

            user_vote = models.Vote.objects.filter(user=profile,meeting_id=meeting_id)
            for v in user_vote:
                voted_slot.append(v.meeting_time_option)
            print('voted_slot: '+ str(len(voted_slot)))
            
            votes = models.Vote.objects.filter(meeting_id=meeting_id)
            print('Number of votes: ' + str(len(votes)))

            #Check if all team member have voted
            if len(votes) == len(members):
                print('All team member have voted')

                # count vote!
                for i in range(len(meeting_time_options)):
                    for vote in votes:
                        if vote.meeting_time_option == meeting_time_options[i]:
                            meeting_time_options[i].vote_count = meeting_time_options[i].vote_count + 1
                            print('Vote_count + 1')
                            print(meeting_time_options[i].start_time)
                            print(meeting_time_options[i].vote_count)
                meeting_time_options.sort(key=lambda MeetingTimeOption:MeetingTimeOption.vote_count, reverse=True)
                if meeting_time_options[0].vote_count == meeting_time_options[1].vote_count :
                    print('Vote Count is equal - Review time slots again')
                    Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.OPEN)
                    fifty_fifty_votes.append(meeting_time_options[0])
                    fifty_fifty_votes.append(meeting_time_options[1])
                    for m in range(len(meeting_time_options)):
                        if m != 0 and m != 1:       
                            if meeting_time_options[0].vote_count == meeting_time_options[m].vote_count:
                                print(m)
                                fifty_fifty_votes.append(meeting_time_options[m])
                    print('fifty_votes: ' + str(len(fifty_fifty_votes)))
                    votes = Vote.objects.filter(meeting=meeting)
                    print('votes length: '+ str(len(votes)))   
                    print('OPS DELETED')
                    ffv = []
                    for v in votes:      
                        ffv.append(MeetingTimeOption(start_time=v.meeting_time_option.start_time,end_time=v.meeting_time_option.end_time,meeting=meeting))
                       
                    ops.delete()
                    for f in ffv:
                        f.save()
                        print('FFV Saved to Database')
                        


                else:
                    
                    meeting = models.Meeting.objects.get(id=meeting_id) if models.Meeting.objects.get(id=meeting_id) else None
                    MeetingTime.objects.filter(meeting=meeting).delete()
                    meeting_time = MeetingTime(start_time=meeting_time_options[0].start_time,
                                                    end_time=meeting_time_options[0].end_time,
                                                    meeting=meeting)
                    meeting_time.save()
                    print('Meeting Time has been assigned')
                    Meeting.objects.filter(id=meeting_id,project=project).update(state=models.Meeting.VoteState.DONE)
                    state_closed = True

        elif meeting.state == CLOSE:
            print('Vote is CLOSE')
            print('Not Ready to vote or you voted')
            
            
        else:
            print('else')
            
        meeting = models.Meeting.objects.get(id=meeting_id) if models.Meeting.objects.get(id=meeting_id) else None
        print('END Meeting Current State is ' + str(meeting.state))

        try:
            mt = models.MeetingTime.objects.get(meeting=meeting)
        except MeetingTime.DoesNotExist:
            pass
            mt = None
         
        context = {
            'active_meeting': active_meeting,
            'meeting_list': avlb_meeting_list,
            'app_url': app_url,
            'time_slots': time_slots,
            'time_slots_json': time_slots_json,
            'team': teamTest, #Instead 'team' For Debug   
            'state_ready': state_ready,
            'meeting_time_slots':meeting_time_slots,
            'meeting_time_options':meeting_time_options,
            'state_no_vote':state_no_vote,
            'state_review':state_review,
            'state_closed':state_closed,
            'voted_slot':voted_slot,
            'votes':votes,
            'fifty_fifty_votes':fifty_fifty_votes,
            'meeting_time':mt,
        }

        return render(request, 'voting/meeting_vote.html', context)

    
    def post(self, request, meeting_id, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        user = request.user if request.user.is_authenticated else None
        profile = pull_profile(user)
        meeting = models.Meeting.objects.get(id=meeting_id) if models.Meeting.objects.get(id=meeting_id) else None
        meeting_time_option_id = int(request.POST.get('id')) if request.POST.get('id') else None
        print('id: ' + str(meeting_time_option_id))

        context = {

            'meeting_id':meeting_id
        }


        meeting_time_option = models.MeetingTimeOption.objects.get(id=meeting_time_option_id, meeting=meeting) if models.MeetingTimeOption.objects.get(id=meeting_time_option_id, meeting=meeting) else None
        if not models.Vote.objects.filter(user=profile,meeting_id=meeting_id):
            vote = Vote(meeting_time_option=meeting_time_option, meeting=meeting, user=profile)
            vote.save()
            print('Vote Saved')
            

        
        if request.POST.get('delete') if request.POST.get('delete') else None:
            print('Vote Deleted')
            Vote.objects.filter(meeting_time_option=meeting_time_option, meeting=meeting, user=profile).delete()




        return HttpResponseRedirect(request.path_info)

def voting(request):
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

    return render(request, 'voting/index.html', context)

def thanks(request, meeting_id):
    if not request.user.is_authenticated:
        return redirect('LoginProcess')
    
    user = request.user if request.user.is_authenticated else None
    
    if user is None:
        return redirect('LoginProcess')
    
    profile = pull_profile(user)

    context = {
        'user': profile ,
        'meeting_id':meeting_id,
    }

    return render(request, 'voting/thanks.html', context)