#!/bin/bash

echo 'run script'
sudo openvpn --config /etc/openvpn/key005/client.ovpn --ca /etc/openvpn/key005/ca.crt --cert /etc/openvpn/key005/key005.crt --key /etc/openvpn/key005/key005.key
