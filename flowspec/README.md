# Overview
This lab demonstrates BGP FlowSpec implementation on Arista cEOS.

## Learning Objectives:
* Configured different BGP FlowSpec actions (discard, redirect).

## Lab consists of following devices:
* `igw`
* `isp`
* `customer`
* `scrubber`
* `exabgp`

## Key protocols used:
* BGP IPv4 unicast address family between `customer`, `igw` and `isp`
* BGP FlowSpec address family between `igw` and `exabgp`

## Lab exercices:
* Lab #1 - FlowSpec discard action
* Lab #2 - FlowSpec redirect to a VRF
