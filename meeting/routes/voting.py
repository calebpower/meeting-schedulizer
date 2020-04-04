from django.shortcuts import render
from django.views.generic import View

from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.models import User

from meeting.forms import MeetingForm
from meeting.models import Meeting
from meeting.views import pull_profile
from meeting.views import get_meetings_by_user

from meeting.models import Vote
from . import models
import datetime
from datetime import datetime, timedelta
import random
import time


class VotingDemo(View):

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
            if timeslots[s].start_time == ts.start_time and timeslots[s].end_time == ts.end_time:
                return True
        return False
    
    #Check if the identical(contains same members) timeslot exists in the given list
    def isIdentical(self, timeslots, ts):
        for s in range(len(timeslots)):
            if timeslots[s].start_time == ts.start_time and timeslots[s].end_time == ts.end_time:
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
    def refine_meeting_time_slots_lst(self, availableTimeSlotsLst):
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
                    if FATS[k].start_time == availableTimeSlots[j].start_time and FATS[k].end_time == availableTimeSlots[j].end_time:
                        flag = False
                        a = FATS[k].members
                        b = availableTimeSlots[j].members
                        if set(a) == set(b):
                            print('')
                            print('   Already exists!!!!!!!!!!!!!!!')

                        else:
                            print(' ')
                            print('a: ' + str(FATS[k].start_time) + '-' + str(
                                FATS[k].end_time) + ' : ',end='')
                            for l in range(len(FATS[k].members)):
                                print(str(FATS[k].members[l] + ' '), end='')
                            print(' ')
                            print('b: ' + str(availableTimeSlots[j].start_time) + '-' + str(
                                availableTimeSlots[j].end_time) + ' : ', end='')
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
    def generate_meeting_time_slots_lst(self,teamMember):
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
            g = self.generate_available_time_slots(permutationlst[p])
            availableTimeSlotsLst.append(g)
        return availableTimeSlotsLst

    #Refine available time slots
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
                print('a: ' + str(ts1.start_time) + '-' + str(ts1.end_time) + ' ', end = '')
                for k in range(len(a)):
                    print(a[k], end='')
                print(' ')
                print('b: ' + str(ts2.start_time) + '-' + str(ts2.end_time) + ' ', end = '')
                for k in range(len(b)):
                    print(b[k], end='')
                print(' ')
                if set(a) == set(b):
                    print('a = b ')
                    if ts1.start_time > ts2.end_time or ts2.start_time > ts1.end_time:
                        print('no overlapping time')
                        print('Do nothing')


                    elif ts1.start_time == ts2.start_time and ts1.end_time == ts2.end_time:
                            print('Same time slot: Do nothing')

                    elif ts1.start_time < ts2.start_time and ts1.end_time < ts2.end_time:
                        if (ts1.end_time - ts2.start_time) < self.MEETING_DURATION:
                            print('Case 1A: Meeting time is ' + str(ts1.end_time -
                            ts2.start_time) + ': Not enough time for meeting')
                        else:
                            # Start time of B and end time of A is overlapping
                            print('Case 1B: Start time of B and end time of A is overlapping')
                            temp = TempTimeSlot(ts1.start_time, ts2.end_time)
                            for k in range(len(b)):
                                temp.members.append(b[k])
                            if not not self.checkSlot(aq, temp):
                                
                                removedLst.append(ts1)
                                removedLst.append(ts2)
                                print(str(ts1.start_time) + '-' + str(ts1.end_time) + ' removed')
                                # timeslots.remove(ts1)
                                aq.append(temp)
                                # timeslots.append(temp)
                                print(str(temp.start_time) + '-' + str(temp.end_time) + ' appended')

                        
                    elif ts1.start_time > ts2.start_time and ts1.end_time > ts2.end_time:
                        if (ts2.end_time - ts1.start_time) < self.MEETING_DURATION:
                            print('Case 2A: Meeting time is ' + str(ts2.end_time -
                                    ts1.start_time) + ': Not enough time for meeting')
                        else:
                            # Start time of A and End time of B is overlapping
                            print('Case 2B: Start time of A and End time of B is overlapping')
                            temp = TempTimeSlot(ts2.start_time, ts1.end_time)
                            for k in range(len(b)):
                                temp.members.append(b[k])
                            if not self.checkSlot(aq, temp):
                                removedLst.append(ts1)
                                removedLst.append(ts2)
                                print(str(ts1.start_time) + '-' + str(ts1.end_time) + ' removed')
                                # timeslots.remove(ts1)
                                # timeslots.append(temp)
                                aq.append(temp)
                                print(str(temp.start_time) + '-' + str(temp.end_time) + ' appended')


                    elif ts1.start_time >= ts2.start_time and ts1.end_time <= ts2.end_time:
                        # Start time of A and End time of A is overlapping
                        print('Case 3: Start time of A and End time of A is overlapping')
                        if not self.checkSlot(removedLst, ts2):
                            removedLst.append(ts1)
                            print(str(ts1.start_time) + '-' + str(ts1.end_time) + ' removed')
                            # timeslots.remove(ts1)


                    elif ts1.start_time <= ts2.start_time and ts1.end_time >= ts2.end_time:
                        # Start time of B and End time of B is overlapping
                        print('Case 4: Start time of B and End time of B is overlapping')
                        print('Do nothing')
                    else:
                        print('Someting wrong')

                elif set(a) - set(b):
                    print('a - b ')
                    print(set(a) - set(b))
                    if ts1.start_time == ts2.start_time and ts1.end_time == ts2.end_time:
                        print('Same time slot')
                        print('Do nothing')
                    else:
                        print('Not same time slot')
                        print('Do nothing')



                elif set(b) - set(a):
                    print('b - a')
                    if ts1.start_time == ts2.start_time and ts1.end_time == ts2.end_time:
                        print('Same time slot')
                        if not self.checkSlot(removedLst, ts2):
                            removedLst.append(ts1)
                            print(str(ts1.start_time) + '-' + str(ts1.end_time) + ' removed')
                            # timeslots.remove(ts1)
                            # timeslots.append(ts2)
                            aq.append(ts2)
                            print(str(ts2.start_time) + '-' + str(ts2.end_time) + ' appended')



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
            if self.checkSlot(timeslots, removedLst[r]):
                timeslots.remove(removedLst[r])
        removedLst.clear()

        for i in range(len(timeslots)):
    
            if len(timeslots[i].members) == 1:
                removedLst.append(timeslots[i])
        for i in range(len(removedLst)):
            timeslots.remove(removedLst[i])

        return timeslots

    #Generate available time slots
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
                                        if not self.checkMember(ts2.members, teamMember[u].name):
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
        t = TempTimeSlot(-1,-1,)
        u = Person(None)

        startTime = request.POST.get('tStart') if request.POST.get('tStart') else None
        endTime = request.POST.get('tEnd') if request.POST.get('tEnd') else None

        t.start_time = int(startTime) if startTime else None
        t.end_time = int(endTime) if endTime else None

        u.name = request.POST.get('user')

        if t.start_time != -1 and u.name != None:
            for user in self.teamMember:
                duplicateSlot = False
                if u.name == user.name:
                    for timeslot in user.timeSlots:
                        if timeslot.start_time == t.start_time and timeslot.end_time == t.end_time: 
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
            g = self.generate_meeting_time_slots_lst(self.teamMember)
            self.refinedSlots = self.refine_meeting_time_slots(self.refine_meeting_time_slots_lst(g))
            

        context = {
            'users':self.users,
            'teamMember':self.teamMember,
            'availableTimeSlots':self.refinedSlots,
        }
        return render(request, 'voting_demo/index.html', context)
    
    def get(self, request):

        context = {
            'users':self.users,
        }
        return render(request, 'voting_demo/index.html', context)

class Person:
    def __init__(self, name):
        self.name = name
        self.isSubmitted = False
        self.isUser = False
        self.timeSlots = []

class TempTimeSlot:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.members = []

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
                for m in t.members:
                    print(m)
                print(' ')


        return availableTimeSlotsLst

    #Generate voting option
    def generate_voting_option(self,start, end):
        timeslots = []
        if abs(end -  start) >= self.MEETING_DURATION and abs(end -  start) < self.MEETING_DURATION*2:
            ds = self.roundup_time(start,end)
            rStart = self.datetime_to_milli(ds)
            rEnd = rStart + self.MEETING_DURATION
            de = self.milli_to_datetime(rEnd)
            timeslots.append(TempTimeSlot(ds, de))

        else:
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
        voting_options = []
        voted_slot = []
        project = None
        profile = None    
        isReady = True
        no_vote = False
        has_voted = False  


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

        meeting = models.Meeting.objects.get(id=meeting_id) if models.Meeting.objects.get(id=meeting_id) else None
        ops = models.MeetingTime.objects.filter(meeting_id=meeting_id)
        print('Voting_options length is '+ str(len(voting_options)))
        for op in ops:
            voting_options.append(op)
        
        # vote = models.Vote.objects.filter(id=meeting_id)
        vote = models.Vote.objects.filter(user=profile)
        for v in vote:
            voted_slot.append(v.meeting_time)
            has_voted = True
       
        
        try:
            project = [meeting for meeting in meeting_list if meeting.id == meeting_id][0].project
            
            members = models.Member.objects.filter(project=project)
            for member in members:
                timeslots = models.TimeAvailability.objects.filter(user=member.user,meeting_id=meeting_id)
                u = Person(member.user.display_name)
                uTest = Person(member.user.display_name) #For Debug
                if member.user.display_name == profile.display_name:
                    u.isUser = True
                    uTest.isUser = True #For Debug
                if timeslots:
                    u.isSubmitted = True
                    uTest.isSubmitted = True  #For Debug                
                    for slot in timeslots:
                        #Convert to milli
                        start = self.datetime_to_milli(slot.start_time)
                        end = self.datetime_to_milli(slot.end_time)
                        t = TempTimeSlot(start, end)
                        t.members.append(member.user.display_name)
                        u.timeSlots.append(t)
                        tTest = TempTimeSlot(slot.start_time, slot.end_time) #For Debug
                        uTest.timeSlots.append(tTest) #For Debug
                        

                else:
                    isReady = False
                team.append(u)
                teamTest.append(uTest)
                
            if isReady and not voting_options:
                ('Generate Voting Option')
                g_asl = self.generate_meeting_time_slots_lst(team)
                r_slots = self.refine_meeting_time_slots(self.refine_meeting_time_slots_lst(g_asl))
                meeting_time_slots = self.find_meeting_slots(r_slots, team)
                print(len(meeting_time_slots))
                print(' ')


        #**************************USE FOR TEST*******************************************]
                # print('*********************TEST**********************************')
                # print(' ')
                # i = 0
                # now = datetime.now()
                # now = now.replace(second=0,microsecond=0)
                # test_slots = []
                # while i < 3:
                #     min = random.randrange(1, 60)
                #     hour = random.randrange(1, 12)
                #     start = int(round(now.timestamp()*1000))
                #     # end = start + self.MEETING_DURATION + (1 * 60 * 1000)
                #     # dEnd = self.milli_to_datetime(end)
                #     # print('now = '+ str(now))
                #     # print('dEnd = '+ str(dEnd))
                #     # print('start random_min = '+ str(min))
                #     # print('start random_hour = '+ str(hour))
                #     start = start + min * 60 * 1000
                #     start = start + hour * 60 * 60 * 1000
                #     min = random.randrange(1, 10)
                #     hour = random.randrange(1)
                #     # print('end random_min = '+ str(min))
                #     # print('end random_hour = '+ str(hour))
                #     # end = start + min * 60 * 1000
                #     # end = start + hour * 60 * 60 * 1000
                #     end= start + self.MEETING_DURATION + min * 60 * 1000
                #     dStart = self.milli_to_datetime(start)
                #     dEnd = self.milli_to_datetime(end)
                #     diff = dEnd - dStart
                #     print('dStart = '+ str(dStart))
                #     print('dEnd = '+ str(dEnd))
                #     print('dStart - dEnd = ' + str(divmod(diff.total_seconds(), 60)) + ' min')
                #     print(' ')
                #     test_slots.append(TempTimeSlot(start, end))
                #     i += 1
                # print('test_slots = ' + str(len(test_slots)))
                # print(' ')
                # for timeslot in test_slots:  
        #****************************END TEST*******************************************

                
                for timeslot in meeting_time_slots:
                

                    start = timeslot.start_time
                    end = timeslot.end_time
                    dStart = self.milli_to_datetime(start)
                    dEnd = self.milli_to_datetime(end)
                    print(' ')
                    print('Before round-up')
                    print(dStart)

                    for option in self.generate_voting_option(start, end):
                        voting_options.append(option)
                print(len(voting_options))

                #Save options to Database
                for op in voting_options:
                    models.MeetingTime.objects.create(start_time=op.start_time,
                                                    end_time=op.end_time,
                                                    meeting=meeting, user=profile)
                    print('option saved to database!')

            elif isReady and voting_options:
                if voted_slot:
                    print('You voted')
                else:
                    print('Start Voting')
                if len(voting_options) == 1:
                    no_vote = True
                    print('No vote needed')

            else:
                print('Not Ready to vote')

        except Exception as e:
            print(e)
            print(' ')

        context = {
            'active_meeting': active_meeting,
            'meeting_list': avlb_meeting_list,
            'app_url': app_url,
            'time_slots': time_slots,
            'time_slots_json': time_slots_json,
            'team': teamTest, #Instead 'team' For Debug   
            'isReady': isReady,
            'meeting_time_slots':meeting_time_slots,
            'voting_options':voting_options,
            'no_vote':no_vote,
            'has_voted':has_voted,
            'voted_slot':voted_slot

        }
        
        return render(request, 'voting/meeting_vote.html', context)
    
    def post(self, request, meeting_id, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        user = request.user if request.user.is_authenticated else None
        profile = pull_profile(user)
        
        if not models.Vote.objects.filter(user=profile):

            meeting = models.Meeting.objects.get(id=meeting_id) if models.Meeting.objects.get(id=meeting_id) else None
            id = request.POST.get('id') if request.POST.get('id') else None
            meeting_time = models.MeetingTime.objects.get(id=id)
            vote = Vote(meeting_time=meeting_time, meeting=meeting, user=profile)
            vote.save()

        context = {
            # 'active_meeting': active_meeting,
            # 'meeting_list': avlb_meeting_list,
            # 'app_url': app_url,
            # 'time_slots': time_slots,
            # 'time_slots_json': time_slots_json,
            # 'team': teamTest, #Instead 'team' For Debug   
            # 'isReady': isReady,
            # 'meeting_time_slots':meeting_time_slots,
            # 'voting_options':voting_options,
            # 'no_vote':no_vote,
        }

        return  render(request, 'voting/thanks.html', context)

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

def thanks(request):
    if not request.user.is_authenticated:
        return redirect('LoginProcess')
    
    user = request.user if request.user.is_authenticated else None
    
    if user is None:
        return redirect('LoginProcess')
    
    profile = pull_profile(user)

    context = {
        'user': profile ,
    }

    return render(request, 'voting/thanks.html', context)