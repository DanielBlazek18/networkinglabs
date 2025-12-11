# Overview
This lab demonstrates BGP RPKI on Arista cEOS. [Routinator](https://github.com/NLnetLabs/routinator) is used as the Relying Party (RP) software, installation guide is [here](https://routinator.docs.nlnetlabs.nl/en/stable/installation.html).

## LAB consists of following devices:
* `inet-r1`
* `inet-r2`
* `isp`
* `core`
* `rpki-rp`

## Key protocols used:
* BGP
* Resource Public Key Infrastructure (RPKI)
* [Routing control functions (RCF)](https://www.arista.com/en/um-eos/eos-routing-control-functions) and standard route-maps

## Setup and test results:
The `isp` router is advertising three prefixes:
```
interface Loopback1
   description Internet-prefix-8.8.8.0m24_demonstration_of_valid
   ip address 8.8.8.8/24
interface Loopback2
   description Internet-prefix-9.9.9.0m24_demonstration_of_invalid
   ip address 9.9.9.9/24
interface Loopback3
   description Internet-prefix-220.150.206.0m23_demonstration_of_unknown
   ip address 220.150.206.1/23
interface Loopback4
   description Internet-prefix-2001:4860::m32_demonstration_of_valid
   ipv6 address 2001:4860:4860::8888/32
interface Loopback5
   description Internet-prefix-2620:fe::m48_demonstration_of_invalid
   ipv6 address 2620:fe::9999/48
interface Loopback6
   description Internet-prefix-2332:1234::m32_demonstration_of_unknown
   ipv6 address 2332:1234::1/32
```

Prefixes advertised to `inet-r1` and `inet-r2`:
```
isp#sh ip bgp neighbors 192.0.0.3 advertised-routes
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      8.8.8.0/24             192.0.0.2             -       -          -       -       15169 i
 * >      9.9.9.0/24             192.0.0.2             -       -          -       -       15169 i
 * >      220.150.206.0/23       192.0.0.2             -       -          -       -       15169 i

isp#sh ipv6 bgp peers 2000::3 advertised-routes 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      2001:4860::/32         2000::2               -       -          -       -       15169 i
 * >      2332:1234::/32         2000::2               -       -          -       -       15169 i
 * >      2620:fe::/48           2000::2               -       -          -       -       15169 i
```

RPKI validation with standard route-map on `inet-r1`:
```
route-map rpki-filter permit 10
   description permit valid prefixes
   match origin-as validity valid
route-map rpki-filter permit 20
   description permit not-found prefixes
   match origin-as validity not-found
route-map rpki-filter deny 30
   description deny invalid prefixes
   match origin-as validity invalid
router bgp 65000
   address-family ipv4
      neighbor 192.0.0.0 route-map rpki-filter in
```

As expected, `inet-r1` install valid and unknown prefixes:
```
inet-r1#sh bgp ipv4 unicast 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      8.8.8.0/24             100.64.0.2            0       -          200     0       15169 i
 *      V 8.8.8.0/24             192.0.0.0             0       -          100     0       15169 i
 * >    U 220.150.206.0/23       192.0.0.0             0       -          100     0       15169 i
 *        220.150.206.0/23       100.64.0.2            0       -          100     0       15169 i

inet-r1#sh bgp ipv6 unicast 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >  L   2001:4860::/32         ::ffff:100.64.0.2     0       -          200     0       15169 i
 *      V 2001:4860::/32         2000::                0       -          100     0       15169 i
 * >    U 2332:1234::/32         2000::                0       -          100     0       15169 i
 *    L   2332:1234::/32         ::ffff:100.64.0.2     0       -          100     0       15169 i
```

The invalid prefix (9.9.9.9/24) is not installed but visible in `recieved-routes`:
```
inet-r1#sh ip bgp neighbors 192.0.0.0 received-routes 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 *      V 8.8.8.0/24             192.0.0.0             -       -          -       -       15169 i
        I 9.9.9.0/24             192.0.0.0             -       -          -       -       15169 i
 * >    U 220.150.206.0/23       192.0.0.0             -       -          -       -       15169 i

inet-r1#sh ipv6 bgp peers 2000:: received-routes 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 *      V 2001:4860::/32         2000::                -       -          -       -       15169 i
 * >    U 2332:1234::/32         2000::                -       -          -       -       15169 i
        I 2620:fe::/48           2000::                -       -          -       -       15169 i
```

Routing Control Function (RCF) on `inet-r2`:
```
router general
   control-functions
      code
      function rpkiFilter() {
          if rpki.match_origin_as_validity( roa_table default, ROA_VALID ) {
              local_preference = 200;
              return true;
          } else if rpki.match_origin_as_validity( roa_table default, ROA_NOT_FOUND ) {
              local_preference = 100;
              return true;
          } else if rpki.match_origin_as_validity( roa_table default, ROA_INVALID ) {
              return false;
          }
          return true;
      }
      EOF
router bgp 65000
   address-family ipv4
      neighbor 192.0.0.2 rcf in rpkiFilter()
```

Valid and unknown prefixes are installed:
```
inet-r2#sh bgp ipv4 unicast 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >    V 8.8.8.0/24             192.0.0.2             0       -          200     0       15169 i
 * >    U 220.150.206.0/23       192.0.0.2             0       -          100     0       15169 i
 *        220.150.206.0/23       100.64.0.1            0       -          100     0       15169 i

inet-r2#sh bgp ipv6 unicast 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >    V 2001:4860::/32         2000::2               0       -          200     0       15169 i
 * >    U 2332:1234::/32         2000::2               0       -          100     0       15169 i
 *    L   2332:1234::/32         ::ffff:100.64.0.1     0       -          100     0       15169 i
```

The invalid prefix is only visible in `recieved-routes`:
```
inet-r2#sh ip bgp neighbors 192.0.0.2 received-routes
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >    V 8.8.8.0/24             192.0.0.2             -       -          -       -       15169 i
        I 9.9.9.0/24             192.0.0.2             -       -          -       -       15169 i
 * >    U 220.150.206.0/23       192.0.0.2             -       -          -       -       15169 i

inet-r2#sh ipv6 bgp peers 2000::2 received-routes 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >    V 2001:4860::/32         2000::2               -       -          -       -       15169 i
 * >    U 2332:1234::/32         2000::2               -       -          -       -       15169 i
        I 2620:fe::/48           2000::2               -       -          -       -       15169 i
```
