# Overview
This lab is testing BGP RPKI on Arista. Routinator has been used for Relying Party software.

## LAB consists of following routers:
* `inet-r1`
* `inet-r2`
* `isp`
* `core`

## Key protocols used:
* BGP
* Resource Public Key Infrastructure (RPKI)
* Routing control functions (RCF) and standard route-maps

## Setup and test results:
`isp` router is advertising three prefixes:
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
```

Prefixes as advertised to `inet-r1` and `inet-r2`:
```
isp#sh ip bgp neighbors 192.0.0.3 advertised-routes
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      8.8.8.0/24             192.0.0.2             -       -          -       -       15169 i
 * >      9.9.9.0/24             192.0.0.2             -       -          -       -       15169 i
 * >      220.150.206.0/23       192.0.0.2             -       -          -       -       15169 i
```

`inet-r1` was configured with standard route-map:
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

As expected, we can see valid and unknow prefixes in the table:
```
inet-r1#sh bgp ipv4 unicast 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      8.8.8.0/24             100.64.0.2            0       -          200     0       15169 i
 *      V 8.8.8.0/24             192.0.0.0             0       -          100     0       15169 i
 * >    U 220.150.206.0/23       192.0.0.0             0       -          100     0       15169 i
 *        220.150.206.0/23       100.64.0.2            0       -          100     0       15169 i
```

And invalid prefix 9.9.9.9/24 can be seen in `recieved-routes`:
```
inet-r1#sh ip bgp neighbors 192.0.0.0 received-routes 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 *      V 8.8.8.0/24             192.0.0.0             -       -          -       -       15169 i
        I 9.9.9.0/24             192.0.0.0             -       -          -       -       15169 i
 * >    U 220.150.206.0/23       192.0.0.0             -       -          -       -       15169 i
```

`inet-r2` was configured with Routing Control Function (RCF):
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

Same as with `inet-r1`, we can see valid and unknow prefixes in the table:
```
inet-r2#sh bgp ipv4 unicast 
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >    V 8.8.8.0/24             192.0.0.2             0       -          200     0       15169 i
 * >    U 220.150.206.0/23       192.0.0.2             0       -          100     0       15169 i
 *        220.150.206.0/23       100.64.0.1            0       -          100     0       15169 i
```

And invalid prefix 9.9.9.9/24 can be seen in `recieved-routes`:
```
[omitted]
          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >    V 8.8.8.0/24             192.0.0.2             -       -          -       -       15169 i
        I 9.9.9.0/24             192.0.0.2             -       -          -       -       15169 i
 * >    U 220.150.206.0/23       192.0.0.2             -       -          -       -       15169 i
```
