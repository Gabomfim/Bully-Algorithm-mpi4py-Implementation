#When a process P recovers from failure, or the failure detector indicates that the current coordinator has failed, P performs the following actions:

#1 - P sends a message to all processes
#2 - Processes with ID bigger than P responds to this call is the leader
#3 - P broadcasts this process as the leader, in its role of election organizer.

from typing import MutableMapping
from mpi4py import MPI
import time

comm = MPI.COMM_WORLD

my_rank = comm.Get_rank()
p = comm.Get_size()
    
electionCaller = 1 #Choose the Election Caller

class Leader:
    id = None

if my_rank == electionCaller:
    reqList = []
    for procid in range(0, p):
        if procid != my_rank:
            message = str(my_rank) + " -> " + str(procid) + ": This is process " + str(my_rank) + ", the election organiser. Process " + str(procid) + ", please respond if you want to take part in the election!\n"
            comm.send(message, dest=procid)
            reqList.append(comm.irecv(source=procid))
    time.sleep(1)
    reqStatus = MPI.Status()
    Leader.id = my_rank
    for request in reqList: # If there was a response, I am not the leader
        ack = request.test(reqStatus)
        leaderCandidate = reqStatus.Get_source()
        if leaderCandidate > Leader.id and ack[0] != False:
            print(ack[1])
            Leader.id = leaderCandidate # Choose the leader

    print("-----------------------------------------------------------------------")
    print("PROCESS " + str(my_rank) + " IN ITS ROLE OF ELECTION ORGANISER, DECLARES " + str(Leader.id) + " AS THE WINNER!!!\n")

    Leader.id = comm.bcast(Leader.id, root=my_rank)

    
else:
    waitResult = False
    while(True):
        if(comm.probe(source=MPI.ANY_SOURCE) and not waitResult): # Received a challenge from other process
            electionStatus = MPI.Status()
            incomingMessage = comm.recv(source=MPI.ANY_SOURCE, status=electionStatus)
            electionOrganizerID = electionStatus.Get_source()
            print(incomingMessage)
            if my_rank > electionOrganizerID:
                responseMessage = str(my_rank) + " -> " + str(electionOrganizerID) + ": Hello process " + str(electionStatus.Get_source()) + ". I, process " + str(my_rank) + ", would like to be a candidate in this election\n" # Responds the challenge with an ACK to assert dominance
                comm.send(responseMessage, dest=electionOrganizerID)
            waitResult = True

        if(waitResult):
            Leader.id = comm.bcast(Leader.id, root=electionOrganizerID) # Election leader will be announced through the election organizer broadcast  
            print("PROCESS " + str(my_rank) + " RECOGNIZES PROCESS " + str(Leader.id) + " AS ITS LEADER!!!\n")