#ifndef TRANSPORTTX
#define TRANSPORTTX

#include <string.h>
#include <omnetpp.h>

using namespace omnetpp;
#include "FeedbackPkt_m.h"

class TransportTx: public cSimpleModule {
private:
    cQueue buffer;
    cMessage *endServiceEvent;
    simtime_t serviceTime;

    // Para análisis
    int sentPackets;
    cOutVector bufferSizeVector;

    bool congestionado;
    simtime_t congestion_window;
    int modifier;

public:
    TransportTx();
    virtual ~TransportTx();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};

Define_Module(TransportTx);

TransportTx::TransportTx() {
    endServiceEvent = NULL;
}

TransportTx::~TransportTx() {
    cancelAndDelete(endServiceEvent);
}

void TransportTx::initialize() {
    buffer.setName("buffer");
    endServiceEvent = new cMessage("endService");

    sentPackets = 0;
    bufferSizeVector.setName("Buffer size");

    congestionado = false;
    congestion_window = 0;
    modifier = 30;
}

void TransportTx::finish() {
    recordScalar("Sent packets", sentPackets);
    recordScalar("Final buffer size", buffer.getLength());
}

void TransportTx::handleMessage(cMessage *msg) {

    if (msg->getKind()==2 && !congestionado){
        congestionado = true;
        congestion_window = simTime() + 6;
    }

    if (congestionado && simTime() >= congestion_window){
        congestionado = false;
    }

    // if msg is signaling an endServiceEvent
    if (msg == endServiceEvent) {
        // if packet in buffer, send next one
        if (!buffer.isEmpty()) {
            // dequeue packet
            cPacket *pkt = (cPacket *)buffer.pop();
            // send packet
            send(pkt, "toOut$o");
            sentPackets++;
            // start new service
            serviceTime = pkt->getDuration();

            // Si esta congestionado subimos el servicetime de los paquetes
            if (congestionado){
                serviceTime = serviceTime*modifier;
            }
            scheduleAt(simTime() + serviceTime, endServiceEvent);
        }
    } else  if (msg->getKind() == 0){ // if msg is a data packet
        if (buffer.getLength() >= par("bufferSize").intValue()) {
            // drop the packet
            delete msg;
            this->bubble("packet dropped");
        } else {
            // enqueue the packet
            buffer.insert(msg);
            bufferSizeVector.record(buffer.getLength());
            // if the server is idle
            if (!endServiceEvent->isScheduled()) {
                // start the service
                scheduleAt(simTime() + 0, endServiceEvent);
            }
        }
    }
}

#endif /* TransportTx */
