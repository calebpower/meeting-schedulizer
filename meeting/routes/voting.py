from django.shortcuts import render
from django.views.generic import View

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
    avaliaveTimeSlots = []
    users = []
    teamMember = []

    def checkMember(self,members, name):
        # print('checkMember is called')
        for m in range(len(members)):
            if members[m] == name:
                # print('Name found !!!!!!!!!!!!!!!')
                return True
        return False

    def checkSlot(self, timeslots, ts):
        # print('checkSlot is called')
        for s in range(len(timeslots)):
            if timeslots[s].tStart == ts.tStart and timeslots[s].tEnd == ts.tEnd:
                # print('Slot found!!!!!!!!!!!!!!!!')
                return True
        return False

    def generateMeeting(self,teamMember):
        u = 0
        rq = []
        aq = []
        avaliaveTimeSlots = self.avaliaveTimeSlots
        while u < len(teamMember):
            k = -1
            # Compare timeslots
            timeslots = teamMember[u].timeSlots
            # print('Available Timeslot Length: ' + str(len(avaliaveTimeSlots)))
            # print(teamMember[u].name + ': TimeSlots' +
            #     ' Length: ' + str(len(timeslots)))
            for i in range(len(avaliaveTimeSlots)):
                # print('Results: ' + str(avaliaveTimeSlots[i].tStart) + '-' + str(
                #     avaliaveTimeSlots[i].tEnd) + ' : ', end='')
                for j in range(len(avaliaveTimeSlots[i].members)):
                    print(str(avaliaveTimeSlots[i].members[j]) + ' ', end='')
                print(' ')
            # Add to array for first iteration
            if len(avaliaveTimeSlots) == 0:
                for s in range(len(timeslots)):
                    avaliaveTimeSlots.append(timeslots[s])
                    avaliaveTimeSlots[len(avaliaveTimeSlots) -
                                    1].members.append(teamMember[u].name)
                    #  print(teamMember[u].name+' slots: ' +
                    #     str(timeslots[s].tStart) + '-' + str(timeslots[s].tEnd))
                    # print(teamMember[u].name + ' added!!!!')
            else:

                for i in range(len(avaliaveTimeSlots)):
                    for j in range(len(timeslots)):

                        k = k + 1
                        ts1 = avaliaveTimeSlots[i]
                        # print('i = ' + str(i))
                        ts2 = timeslots[j]
                        # print('j = ' + str(j))
                        # print('k = ' + str(k))
                        # print('Slot' + str(k) + ': ')
                        # print('Available slots: ' + str(avaliaveTimeSlots[i].tStart) + '-' + str(
                        #     avaliaveTimeSlots[i].tEnd) + ' : ', end='')
                        # for m in range(len(avaliaveTimeSlots[i].members)):
                        #     print(avaliaveTimeSlots[i].members[m] + ' ', end='')
                        # print(' ')
                        # print(teamMember[u].name+' slots: ' +
                        #     str(timeslots[j].tStart) + '-' + str(timeslots[j].tEnd))
                        if not self.checkMember(avaliaveTimeSlots[i].members, teamMember[u].name):
                            # Compare each time slot
                            if ts1.tStart > ts2.tEnd or ts2.tStart > ts1.tEnd:
                                # no overlapping time
                                # print('Case 5: No overlapping periods')
                                if not self.checkSlot(aq, ts2):
                                    ts2.members.append(teamMember[u].name)
                                    aq.append(ts2)
                                    # print(teamMember[u].name + ' added!!!!')
                                    # print('Appended ts2')
                                if not self.checkSlot(aq, ts1):
                                    aq.append(ts1)
                                    # print('Appended ts1')
                                if j == 0:
                                    rq.append(avaliaveTimeSlots[i])

                            elif ts1.tStart == ts2.tStart and ts1.tEnd == ts2.tEnd:
                                # same time slot
                                # print('Case 0: This is same time slot')
                                # print('Meeting time is avaliave from ' +
                                #     str(ts1.tStart) + ' to ' + str(ts1.tEnd))
                                ts = TestTimeSlot(ts1.tStart, ts1.tEnd, 1)
                                for m in range(len(avaliaveTimeSlots[i].members)):
                                    ts.members.append(
                                        avaliaveTimeSlots[i].members[m])
                                if not self.checkMember(ts.members, teamMember[u].name):
                                    ts.members.append(teamMember[u].name)
                                    # print(teamMember[u].name + ' added!!!!')
                                if j == 0:

                                    rq.append(avaliaveTimeSlots[i])
                                    aq.append(ts)

                                else:
                                    aq.append(ts)

                            elif ts1.tStart < ts2.tStart and ts1.tEnd < ts2.tEnd:
                                if (ts1.tEnd - ts2.tStart) < self.MEETING_DURATION:
                                    # print('Case 1A: Meeting time is ' + str(ts1.tEnd -
                                    #                                         ts2.tStart) + ': Not enough time for meeting')
                                    if not self.checkSlot(aq, ts2):
                                        ts2.members.append(teamMember[u].name)
                                        aq.append(ts2)
                                        # print('Appended ts2')
                                    if not self.checkSlot(aq, ts1):
                                        aq.append(ts1)
                                        # print('Appended ts1')
                                    if j == 0:
                                        rq.append(avaliaveTimeSlots[i])

                                else:
                                    # Start time of B and end time of A is overlapping
                                    # print(
                                    #     'Case 1B: Start time of B and end time of A is overlapping')
                                    # print('Meeting time is avaliave from ' +
                                    #     str(ts2.tStart) + ' to ' + str(ts1.tEnd))
                                    ts = TestTimeSlot(ts2.tStart, ts1.tEnd, 0)
                                    for m in range(len(avaliaveTimeSlots[i].members)):
                                        ts.members.append(
                                            avaliaveTimeSlots[i].members[m])
                                    if not self.checkMember(ts.members, teamMember[u].name):
                                        ts.members.append(teamMember[u].name)
                                        # print(teamMember[u].name + ' added!!!!')
                                    if j == 0:
                                        rq.append(avaliaveTimeSlots[i])
                                        aq.append(ts)
                                    else:
                                        aq.append(ts)

                            elif ts1.tStart > ts2.tStart and ts1.tEnd > ts2.tEnd:
                                if (ts2.tEnd - ts1.tStart) < self.MEETING_DURATION:
                                    # print('Case 2A: Meeting time is ' + str(ts2.tEnd -
                                    #                                         ts1.tStart) + ': Not enough time for meeting')
                                    if not self.checkSlot(aq, ts2):
                                        ts2.members.append(teamMember[u].name)
                                        aq.append(ts2)
                                        # print('Appended ts2')
                                    if not self.checkSlot(aq, ts1):
                                        aq.append(ts1)
                                        # print('Appended ts1')
                                    if j == 0:
                                        rq.append(avaliaveTimeSlots[i])

                                else:
                                    # Start time of A and End time of B is overlapping
                                    # print(
                                    #     'Case 2B: Start time of A and End time of B is overlapping')
                                    # print('Meeting time is avaliave from ' +
                                    #     str(ts1.tStart) + ' to ' + str(ts2.tEnd))
                                    ts = TestTimeSlot(ts1.tStart, ts2.tEnd, 1)
                                    for m in range(len(avaliaveTimeSlots[i].members)):
                                        ts.members.append(
                                            avaliaveTimeSlots[i].members[m])
                                    if not self.checkMember(ts.members, teamMember[u].name):
                                        ts.members.append(teamMember[u].name)
                                        # print(teamMember[u].name + ' added!!!!')
                                    if j == 0:

                                        rq.append(avaliaveTimeSlots[i])
                                        aq.append(ts)

                                    else:
                                        aq.append(ts)

                            elif ts1.tStart >= ts2.tStart and ts1.tEnd <= ts2.tEnd:
                                # Start time of A and End time of A is overlapping
                                # print(
                                #     'Case 3: Start time of A and End time of A is overlapping')
                                # print('Meeting time is avaliave from ' +
                                #     str(ts1.tStart) + ' to ' + str(ts1.tEnd))
                                ts = TestTimeSlot(ts1.tStart, ts1.tEnd, 1)
                                for m in range(len(avaliaveTimeSlots[i].members)):
                                    ts.members.append(
                                        avaliaveTimeSlots[i].members[m])
                                if not self.checkMember(ts.members, teamMember[u].name):
                                    ts.members.append(teamMember[u].name)
                                    # print(teamMember[u].name + ' added!!!!')
                                if j == 0:
                                    rq.append(avaliaveTimeSlots[i])
                                    aq.append(ts)
                                else:
                                    aq.append(ts)

                            elif ts1.tStart <= ts2.tStart and ts1.tEnd >= ts2.tEnd:
                                # Start time of B and End time of B is overlapping
                                # print(
                                #     'Case 4: Start time of B and End time of B is overlapping')
                                # print('Meeting time is avaliave from ' +
                                #     str(ts2.tStart) + ' to ' + str(ts2.tEnd))
                                ts = TestTimeSlot(ts2.tStart, ts2.tEnd, 1)
                                for m in range(len(avaliaveTimeSlots[i].members)):
                                    ts.members.append(
                                        avaliaveTimeSlots[i].members[m])
                                if not self.checkMember(ts.members, teamMember[u].name):
                                    ts.members.append(teamMember[u].name)
                                    # print(teamMember[u].name + ' added!!!!')
                                if j == 0:
                                    rq.append(avaliaveTimeSlots[i])
                                    aq.append(ts)
                                else:
                                    aq.append(ts)

                            li = len(avaliaveTimeSlots) - 1
                            lj = len(timeslots) - 1
                            # print('j = ' + str(j) + ': len(timeslots) - 1 = ' + str(lj))
                            if len(rq) != 0 and li == i and lj == j:
                                for r in range(len(rq)):
                                    # print(str(rq[r].tStart) + '-' +
                                    #     str(rq[r].tEnd) + ' is removed!!')
                                    avaliaveTimeSlots.remove(rq[r])
                                rq = []
                            if len(aq) != 0 and li == i and lj == j:
                                for a in range(len(aq)):
                                    # if not checkMember(aq[a].members, teamMember[u].name):
                                    # aq[a].members.append(teamMember[u].name)
                                    # print(teamMember[u].name + ' added!!!!')
                                    avaliaveTimeSlots.append(aq[a])
                                    # print(str(aq[a].tStart) + '-' +
                                    #     str(aq[a].tEnd) + ' is appended!')
                                aq = []
                            # print('Count is ' + str(len(avaliaveTimeSlots)))

            u += 1

    def post(self, request,):
        duplicateSlot = False
        duplicateName = False
        userFound = False
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
        print(type(t.tStart))
        print(type(t.tEnd))
        startTime = request.POST.get('tStart') if request.POST.get('tStart') else None
        endTime = request.POST.get('tEnd') if request.POST.get('tEnd') else None
        print(type(startTime))
        print(type(endTime))
        t.tStart = int(startTime) if startTime else None
        t.tEnd = int(endTime) if endTime else None
        print(type(t.tStart))
        print(type(t.tEnd))
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
                        # u.timeSlots.append(t)
                        # self.teamMember.userappend(u)
                        user.timeSlots.append(t)
                        duplicateSlot = False
                    userFound = True 
            if not userFound:
                u.timeSlots.append(t)
                self.teamMember.append(u)
            # print(len(self.teamMember))
            # print(self.teamMember[len(self.teamMember)-1].timeSlots[0].tEnd)
        # print(add_name)
        # print(u, t.tStart, t.tEnd)
        value = request.POST.get('generate')
        print(value)
        if value == 'g':
            print('generateMeeting is called')
            self.generateMeeting(self.teamMember)

        context = {
            'users':self.users,
            'teamMember':self.teamMember,
            'availableTimeSlots':self.avaliaveTimeSlots
        }
        return render(request, 'voting/index.html', context)
    
    def get(self, request):

        context = {
            'users':self.users,
        }
        return render(request, 'voting/index.html', context)
    