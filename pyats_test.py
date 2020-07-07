import re
from pyats import aetest
from unicon.core.errors import SubCommandFailure
from helpers import banner


class CommonSetup(aetest.CommonSetup):
    """ Common Setup Section """
    @aetest.subsection
    def check_topology(self, testbed,
                       ios_device1='SOHO',
                       ios_device2='ISP1',
                       ios_device3='ISP2'):
        """ Checking topology mapping """
        router_soho = testbed.devices[ios_device1]
        router_isp1 = testbed.devices[ios_device2]
        router_isp2 = testbed.devices[ios_device3]

        self.parent.parameters.update(router_soho=router_soho,
                                      router_isp1=router_isp1,
                                      router_isp2=router_isp2)

        links = [router_soho.find_links(router_isp1),
                 router_isp1.find_links(router_isp2),
                 router_isp2.find_links(router_soho)]
        msg = 'at least one link is required between each device'
        assert len(links) >= 3, msg

    @aetest.subsection
    def establish_connections(self, steps, router_soho,
                              router_isp1, router_isp2):
        """ Checking possibility for connection to all devices """
        with steps.start('Connecting to %s' % router_soho.name):
            router_soho.connect()

        with steps.start('Connecting to %s' % router_isp1.name):
            router_isp1.connect()

        with steps.start('Connecting to %s' % router_isp2.name):
            router_isp2.connect()


@aetest.loop(uids=['test_ping_soho', 'test_ping_isp1', 'test_ping_isp2'],
             router=['router_soho', 'router_isp1', 'router_isp2'])
class PingTestCase(aetest.Testcase):
    """" Test possibility to pinging between devices """
    @aetest.setup
    def setup(self, router):
        """" Setup for PingTestCase """
        ips = set()
        current_router = self.parent.parameters[router]
        testbed = self.parent.parameters['testbed']
        for link in testbed.links:
            if current_router.name.lower() not in str(link):
                continue
            for port in link.interfaces:
                if port.ipv4.is_loopback:
                    continue
                ips.add(port.ipv4.ip.compressed)
        aetest.loop.mark(self.ping, ips=ips)

    @aetest.test
    def ping(self, router, ips):
        """"Test to ping router"""
        try:
            self.parameters[router].ping(ips)
        except SubCommandFailure:
            self.failed('Ping {} from device {} failed with error: {}'.format(
                ips,
                router,
                SubCommandFailure,
                ))


 @aetest.loop(uids=['test_tftp_soho', 'test_tftp_isp1', 'test_tftp_isp2'],
              router=['router_soho', 'router_isp1', 'router_isp2'])
 class TestCaseTftp(aetest.Testcase):
     """T2. make backup to the TFTP server and restore it.
     - add verification that config restored correctly (try use loop
     for customizing config, for example, change banner message).
     """

     @aetest.test
     def test_tftp_backup(self, router):
         """Change Banner and upload backup to tftp server"""
         try:
             # set banner
             self.parent.my_banner = banner.get_banner()
             self.parent.parameters[router].configure(
                 f'banner motd "{self.parent.my_banner}"')
             # backup
             srv_adr = self.parent.parameters['testbed'].servers.filesrv.address
             self.parent.parameters[router].configure("file prompt quiet")
             self.parent.parameters[router].execute(
                 f"copy running-config tftp://{srv_adr}/{router}")
         except SubCommandFailure:
             self.failed('smth bad happened with tftp server :c')

     @aetest.test
     def test_tftp_restore(self, router):
         """Restore config from tftp server and verify that banner msg is present
         """
         try:
             # restore
             srv_adr = self.parent.parameters['testbed'].servers.filesrv.address
             self.parent.parameters[router].execute(
                 f"copy tftp://{srv_adr}/{router} startup-config")
             self.parent.parameters[router].configure("file prompt alert")
             # verify my_banner is in startup config
             config = self.parent.parameters[router].execute(
                 "show startup-config")
             banner_regex = re.compile(r"""banner\smotd\s\^C(.*)\^C""")
             results = banner_regex.search(config)
             msg = (
                 f"startup-banner is: {results},"
                 f"expected-banner is: {self.parent.my_banner}")
             assert self.parent.my_banner == results.group(1), msg

         except SubCommandFailure:
             self.failed('backup download from tftp server failed')
         except AttributeError:
             self.failed('Regex failed to find any results of "banner motd"')


 @aetest.loop(uids=['testValidIntSoho', 'testValidIntIsp1', 'testValidIntIsp2'],
              router=['router_soho', 'router_isp1', 'router_isp2'])
 class TestCaseValidateInterface(aetest.Testcase):
     """T3. Validate interface ip/mask/gateway
     Compare show run interface ip/subnet/gateway and the same information
     extracted from sh ip int brief
     """

     @aetest.setup
     def setup(self, router):
         """gather info about sh ip in br"""
         result_showip = self.parent.parameters[router].execute("sh ip in br")
         interface_regex = re.compile(r"""(\w*\d+/\d+)\s*         # interface
                                          (\d+\.?\d+\.?\d+\.?\d+) # ip address
                                          .*\n                    # else
                                          """, re.VERBOSE)
         interface_ip = interface_regex.findall(result_showip)
         aetest.loop.mark(self.test_compare_show_run, interface_ip=interface_ip)

     @aetest.test
     def test_compare_show_run(self, router, interface_ip):
         """ Compare results of "ip interface brief" with "show run interface"
         """
         show_run = self.parent.parameters[router].execute(
             f"show run interface {interface_ip[0]}")
         ip_regex = re.compile(r"ip\saddress\s(\d+\.?\d+\.?\d+\.?\d+)")
         result = ip_regex.search(show_run)
         assert interface_ip[1] == result.group(1)


class CommonCleanup(aetest.CommonCleanup):
    """ Disconnect from all devices """
    @aetest.subsection
    def disconnect(self, steps, router_soho, router_isp1, router_isp2):
        with steps.start('Disconnecting from %s' % router_soho.name):
            router_soho.disconnect()

        with steps.start('Disconnecting from %s' % router_isp1.name):
            router_isp1.disconnect()

        with steps.start('Disconnecting from %s' % router_isp2.name):
            router_isp2.disconnect()


if __name__ == '__main__':
    import argparse
    from pyats.topology import loader

    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create handler
    fh = logging.FileHandler('my_logs.log')
    fh.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        "*"*80 + "\n" +
        '%(asctime)s - %(name)s - %(levelname)s -:::%(message)s' +
        "\n" + "*"*80)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.debug("start!")

    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)
    args, unknown = parser.parse_known_args()
    aetest.main(**vars(args))
