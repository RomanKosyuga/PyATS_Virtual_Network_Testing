# Introduction

Training project for mastering PyATS testing ecosystem on the topology created in the graphical network simulator GNS3

## Requirements

* [Vagrant](https://www.vagrantup.com/downloads.html) (used version 2.2.9)
* [Oracle VM VirtualBox](https://www.virtualbox.org/wiki/Downloads) (used version 6.1.6)
* [GNS3](https://www.gns3.com/software) (used version 2.2.8)

## Project deploy / usage
#### pyATS environment
```bash
vagrant up
vagrant ssh
cd /vagrant/
python3 connectivity_test.py --testbed pyats_testbed.yaml
```
#### locally running devices may be accessed from a guestOS using Default Gateway 10.0.2.2:
```bash
telnet localhost 5000
telnet 10.0.2.2 5000
```

#### GNS3 environment
File -> Import portable project -> open pyats_testbed1.gns3project<br />
This project without images, so you must have  c7200-jk9s-mz.124-13b.image for Cisco 7200 routers and [Ubuntu Desktop Guest applience](https://www.gns3.com/marketplace/appliance/ubuntu-with-gui)



## Topology (irrelevant, in developing)
                        localhost:5002                             localhost:5003
                       +-------------+                            +-------------+
                       |   Router    | s0/1                  s1/0 |    Router   |
                       |             | —— —— —— —— —— —— —— —— —— |             |
                       | Cisco 7200  |                            |  Cisco 7200 |
                       +-------------+                            +-------------+
                                 s1/1 \                          / s1/2
                                       \      200.1.1.0/24      /
                                        \                      /
                                         \                    /
                                          \                  /                 
                                           \+--------------+/
                                        s1/1|    Router    |s1/2
                                            |              |
                                            |  Cisco 7200  |
                                            +--------------+
                                             localhost:5004
