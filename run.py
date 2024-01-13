# coding=utf-8
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import dpid as dpid_lib
from ryu.lib import stplib
from ryu.lib.packet import packet, ethernet

import socket
from ryu.cmd import manager
# Import the necessary libraries
import socket
from ryu.lib import hub
from ryu.controller import dpset
from ryu.app.wsgi import ControllerBase, WSGIApplication, route

# RestController to handle inter-controller communication
class InterControllerRest(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(InterControllerRest, self).__init__(req, link, data, **config)
        self.dpset = data[dpset.DPSet.__name__]

    # REST API to receive messages from other controllers
    @route('controller', '/inter_controller_message', methods=['POST'])
    def inter_controller_message(self, req, **kwargs):
        try:
            # Extract the message from the request
            msg = req.json if req.body else None
            if msg:
                self.send_message_to_controllers(msg)
                return 'Message sent to other controllers\n'
            else:
                return 'Invalid message format\n'
        except Exception as e:
            return f'Error: {str(e)}\n'

    # Method to send a message to other controllers
    def send_message_to_controllers(self, message):
        for dp in self.dpset.get_all():
            # Assuming each datapath has a unique ID (modify as needed)
            controller_id = dp.id
            if controller_id != self.dp.id:
                self.send_message(dp, message)

    # Method to send a message to a specific controller
    def send_message(self, datapath, message):
        # Modify this method based on your communication mechanism
        # This could involve sockets, REST APIs, or other communication methods
        # For simplicity, this example uses a socket connection to port 9999
        try:
            sock = socket.create_connection(('127.0.0.1', 9999))
            sock.sendall(message.encode())
            sock.close()
        except Exception as e:
            print(f"Error sending message to controller {datapath.id}: {str(e)}")

class IDSClients(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'stplib': stplib.Stp, 'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(IDSClients, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.stp = kwargs['stplib']

        # Instantiate and connect to IDS server
        self.ids_client = IDSClient('127.0.1.1', 9999)
        self.connect_to_ids_server()

        # WSGI Application for inter-controller communication
        wsgi = kwargs['wsgi']
        wsgi.register(InterControllerRest, {'app': self, 'dpset': self.dpset})

    # Existing methods remain unchanged

    # Method to send a message to other controllers
    def send_message_to_controllers(self, message):
        self.logger.info("Sending message to other controllers: %s", message)
        hub.spawn(self.ids_client.send_message_to_controllers, message)

    # Method to send a message to a specific controller
    def send_message_to_controller(self, datapath, message):
        self.logger.info("Sending message to Controller %s: %s", datapath.id, message)
        hub.spawn(self.ids_client.send_message, datapath, message)

    # Existing methods remain unchanged


class IDSClients(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'stplib': stplib.Stp}

    def __init__(self, *args, **kwargs):
        super(IDSClients, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.stp = kwargs['stplib']

        config = {
            dpid_lib.str_to_dpid('0000000000000001'): {'bridge': {'priority': 0x8000}},
            dpid_lib.str_to_dpid('0000000000000002'): {'bridge': {'priority': 0x9000}},
            dpid_lib.str_to_dpid('0000000000000003'): {'bridge': {'priority': 0xa000}}
        }
        self.stp.set_config(config)

        # Instantiate and connect to IDS server
        self.ids_client = IDSClient('127.0.1.1', 9999)
        self.connect_to_ids_server()

    def connect_to_ids_server(self):
        self.ids_client.connect()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        if buffer_id:
            mod = parser.OFPFlowMod(
                datapath=datapath, buffer_id=buffer_id, priority=priority,
                match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority,
                match=match, instructions=inst)

        datapath.send_msg(mod)

    def delete_flow(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        for dst in self.mac_to_port[datapath.id].keys():
            match = parser.OFPMatch(eth_dst=dst)
            mod = parser.OFPFlowMod(
                datapath, command=ofproto.OFPFC_DELETE,
                out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
                priority=1, match=match)
            datapath.send_msg(mod)

    @set_ev_cls(stplib.EventPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(stplib.EventTopologyChange, MAIN_DISPATCHER)
    def _topology_change_handler(self, ev):
        dp = ev.dp
        dpid_str = dpid_lib.dpid_to_str(dp.id)
        msg = 'Receive topology change event. Flush MAC table.'
        self.logger.debug("[dpid=%s] %s", dpid_str, msg)

        if dp.id in self.mac_to_port:
            self.delete_flow(dp)
            del self.mac_to_port[dp.id]

    @set_ev_cls(stplib.EventPortStateChange, MAIN_DISPATCHER)
    def _port_state_change_handler(self, ev):
        dpid_str = dpid_lib.dpid_to_str(ev.dp.id)
        of_state = {stplib.PORT_STATE_DISABLE: 'DISABLE',
                    stplib.PORT_STATE_BLOCK: 'BLOCK',
                    stplib.PORT_STATE_LISTEN: 'LISTEN',
                    stplib.PORT_STATE_LEARN: 'LEARN',
                    stplib.PORT_STATE_FORWARD: 'FORWARD'}
        self.logger.debug("[dpid=%s][port=%d] state=%s",
                          dpid_str, ev.port_no, of_state[ev.port_state])

class IDSClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.ids_socket = None

    def connect(self):
        self.ids_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ids_socket.connect((self.server_ip, self.server_port))
        message = "Hello from Ryu controller!"
        self.ids_socket.sendall(message.encode())
        response = self.ids_socket.recv(1024)
        print(f"Received response from IDS server: {response.decode()}")
        self.ids_socket.close()

if __name__ == "__main__":
    manager.main()
