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

def callElection():
    reqList = []
    for procid in range(my_rank+1, p):
        message = "Received by process " + str(procid) + ": I, process " + str(my_rank) + ", challenge you!!!\n"
        comm.send(message, dest=procid)
        reqList.append(comm.irecv(source=procid))
    time.sleep(5)
    leaderFlag = True
    for request in reqList:
        ack = request.test()
        if ack[0]: # If there was a response, I am not the leader
            print(ack[1])
            leaderFlag = False

    if leaderFlag:
        print("------------------------------------------------")
        print("PROCESS " + str(my_rank) + " IS THE LEADER, AND ANNOUNCES HIS PLAN TO WORLD DOMINATION\n")
        for procid in range(my_rank+1, p):
            leaderAnnouncement = str(procid) + " recognizes process " + str(my_rank) + " as its supreme leader\n"
            comm.send(leaderAnnouncement, dest=procid)
    
    return leaderFlag
            
   


if my_rank == electionCaller:
    # Challenge other processes to see if I am the leader
    leaderFlag = callElection()
    if(not leaderFlag):
        print("process " + str(my_rank) + " recognizes his weakness and is looking for a leader\n")

    while(True): # Wait for the leader while doing tasks as normal
        if(comm.probe(source=MPI.ANY_SOURCE)):
            leaderMessage = comm.recv(source=MPI.ANY_SOURCE) # Implement broadcast later
            print(leaderMessage)
    
else:
    leaderFlag = False
    while(True):
        if(comm.probe(source=MPI.ANY_SOURCE) and not leaderFlag): # Received a challenge from other process
            incomingMessageStatus = MPI.Status()
            incomingMessage = comm.recv(source=MPI.ANY_SOURCE, status=incomingMessageStatus)
            print(incomingMessage)
            responseMessage = "Process " + str(incomingMessageStatus.Get_source()) + ", you are not my leader, this is " + str(my_rank) + "\n" # Responds the challenge with an ACK to assert dominance
            comm.send(responseMessage, dest=incomingMessageStatus.Get_source())

            # Challenge other processes to see if I am the leader
            leaderFlag = callElection()
            if(not leaderFlag):
                print("process " + str(my_rank) + " recognizes his weakness and is looking for a leader\n")

        if(comm.probe(source=MPI.ANY_SOURCE) and leaderFlag):
            leaderMessage = comm.recv(source=MPI.ANY_SOURCE) # Implement broadcast later
            print(leaderMessage)
            leaderFlag = False