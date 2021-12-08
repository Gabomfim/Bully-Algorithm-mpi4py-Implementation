#When a process P recovers from failure, or the failure detector indicates that the current coordinator has failed, P performs the following actions:

#1 - If P has the highest process ID, it sends a Victory message to all other processes and becomes the new Coordinator. Otherwise, P broadcasts an Election message to all other processes with higher process IDs than itself.
#2 - If P receives no Answer after sending an Election message, then it broadcasts a Victory message to all other processes and becomes the Coordinator.
#3 - If P receives an Answer from a process with a higher ID, it sends no further messages for this election and waits for a Victory message. (If there is no Victory message after a period of time, it restarts the process at the beginning.)
#4 - If P receives an Election message from another process with a lower ID it sends an Answer message back and starts the election process at the beginning, by sending an Election message to higher-numbered processes.
#5 - If P receives a Coordinator message, it treats the sender as the coordinator.

from mpi4py import MPI
import time

comm = MPI.COMM_WORLD

my_rank = comm.Get_rank()
p = comm.Get_size()
    
electionCaller = 0

if my_rank == electionCaller:
    reqList = []
    for procid in range(my_rank+1, p):
        message = "I, process " + str(my_rank) + ", challenge you!!!"
        comm.send(message, dest=procid)
        reqList.append(comm.irecv(source=procid))
    time.sleep(2)
    leaderFlag = True
    for request in reqList:
        if request.test(): # If there was a response, I am not the leader
            leaderFlag = False
    
    if leaderFlag:
        print("------------------------------------------------")
        print("PROCESS " + str(my_rank) + " ANNOUNCES HIS PLAN TO WORLD DOMINATION")
        for procid in range(my_rank+1, p):
            leaderAnnouncement = str(procid) + "recognizes process " + str(my_rank) + " as its supreme leader"
            comm.send(leaderAnnouncement, dest=procid)
    
    while(True): # Wait for the leader while doing tasks as normal
        if(comm.probe):
            leaderMessage = comm.recv(source=MPI.ANY_SOURCE) # Implement broadcast later
            print(leaderMessage)
    
    
else:
    while(True):
        if(comm.probe(source=MPI.ANY_SOURCE)): # Received a challenge from other process
            incomingMessageStatus = MPI.Status()
            incomingMessage = comm.recv(source=MPI.ANY_SOURCE, status=incomingMessageStatus)
            print(incomingMessage)
            responseMessage = "You are not my leader, this is " + str(my_rank) # Responds the challenge with an ACK to assert dominance
            comm.isend(responseMessage, dest=incomingMessageStatus.Get_source())

            # Challenge other processes to see if I am the leader
            reqList = []
            for procid in range(my_rank+1, p):
                message = "I, process " + str(my_rank) + ", challenge you!!!"
                comm.send(message, dest=procid)
                reqList.append(comm.irecv(source=procid))
            time.sleep(2)
            leaderFlag = True
            for request in reqList:
                if request.test(): # If there was a response, I am not the leader
                    leaderFlag = False
            
            if leaderFlag:
                print("------------------------------------------------")
                print("PROCESS " + str(my_rank) + " ANNOUNCES HIS PLAN TO WORLD DOMINATION")
                for procid in range(my_rank+1, p):
                    leaderAnnouncement = str(procid) + "recognizes process " + str(my_rank) + " as its supreme leader"
                    comm.send(leaderAnnouncement, dest=procid)
            
            while(True): # Wait for the leader while doing tasks as normal
                if(comm.probe):
                    leaderMessage = comm.recv(source=MPI.ANY_SOURCE) # Implement broadcast later
                    print(leaderMessage)