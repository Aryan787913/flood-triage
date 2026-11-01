# Robustness check: real Indian monsoon street photos (qualitative)

20 photos from Wikimedia Commons (Chennai, Mumbai, Kerala, Hyderabad floods). Full street scenes, not vehicle crops, so this is out of distribution for the reference examples. No ground truth: this is a qualitative look, not a benchmark. Images are not committed; each is linked to its Commons page with its licence and author.

| # | Commons file | Licence | Spark (3 reads) | Final | Evidence / reason |
|---|---|---|---|---|---|
| 3 | [Chennai floods Dec 2005.jpg](https://commons.wikimedia.org/wiki/File:Chennai_floods_Dec_2005.jpg) (MPVK) | CC BY-SA 4.0 | X, 2, 2 | L2 | water halfway up tricycle wheels, chassis just above |
| 5 | [India - Chennai - Monsoon - 02 (3059047958).jpg](https://commons.wikimedia.org/wiki/File:India_-_Chennai_-_Monsoon_-_02_(3059047958).jpg) (McKay Savage from London, UK) | CC BY 2.0 | 1, 1, 1 | L1 | Shallow brown floodwater touches lower motorcycle tyres on street |
| 6 | [India - Chennai - Monsoon - 03 (3058213357).jpg](https://commons.wikimedia.org/wiki/File:India_-_Chennai_-_Monsoon_-_03_(3058213357).jpg) (McKay Savage from London, UK) | CC BY 2.0 | 1, 1, 1 | L1 | water covers lower third of rear tyres, chassis dry |
| 7 | [India - Chennai - Monsoon - 04 (3058215637).jpg](https://commons.wikimedia.org/wiki/File:India_-_Chennai_-_Monsoon_-_04_(3058215637).jpg) (McKay Savage from London, UK) | CC BY 2.0 | X, X, 1 | can't tell | readings disagree (None, None, 1) |
| 9 | [India - Chennai - Monsoon - 07 (3059060932).jpg](https://commons.wikimedia.org/wiki/File:India_-_Chennai_-_Monsoon_-_07_(3059060932).jpg) (McKay Savage from London, UK) | CC BY 2.0 | 1, 1, 1 | L1 | murky standing water covering lower third of motorbike tyres |
| 12 | [India - Chennai - Monsoon - 10 (3058291559).jpg](https://commons.wikimedia.org/wiki/File:India_-_Chennai_-_Monsoon_-_10_(3058291559).jpg) (McKay Savage from London, UK) | CC BY 2.0 | 1, X, X | can't tell | readings disagree (1, None, None) |
| 13 | [Inundation of Chennai in 2017-1.jpg](https://commons.wikimedia.org/wiki/File:Inundation_of_Chennai_in_2017-1.jpg) (Kaitha Poo Manam) | CC BY-SA 4.0 | X, X, X | can't tell | no distinct vehicle, only flooded waste containers visible |
| 14 | [Inundation of Chennai in 2017-2.jpg](https://commons.wikimedia.org/wiki/File:Inundation_of_Chennai_in_2017-2.jpg) (Kaitha Poo Manam) | CC BY-SA 3.0 | 1, 2, 2 | L2 | Muddy water halfway up motorcycle tyres in flooded street |
| 21 | [A Santro that went "off road" (35520266).jpg](https://commons.wikimedia.org/wiki/File:A_Santro_that_went_%22off_road%22_(35520266).jpg) (Rakesh from Bangalore) | CC BY-SA 2.0 | 0, 0, 0 | L0 | wet muddy road no standing water on tyres or doors |
| 22 | [An ST bus near the WEH flyover at Borivali (35520283).j](https://commons.wikimedia.org/wiki/File:An_ST_bus_near_the_WEH_flyover_at_Borivali_(35520283).jpg) (Rakesh from Bangalore) | CC BY-SA 2.0 | X, X, X | can't tell | vehicle or waterline not visible |
| 23 | [An ST bus near the WEH flyover at Borivali (35520287).j](https://commons.wikimedia.org/wiki/File:An_ST_bus_near_the_WEH_flyover_at_Borivali_(35520287).jpg) (Rakesh from Bangalore) | CC BY-SA 2.0 | 1, 1, 1 | L1 | Shallow puddle at front bumper below half tyre height |
| 24 | [Bombay flooded street.jpg](https://commons.wikimedia.org/wiki/File:Bombay_flooded_street.jpg) () | CC BY 2.0 | X, 1, 1 | L1 | Red bus front, water covers lower tyre below bumper |
| 25 | [Bombay flooded street2.jpg](https://commons.wikimedia.org/wiki/File:Bombay_flooded_street2.jpg) () | CC BY 2.0 | 1, 1, 1 | L1 | ankle-deep floodwater splashing around tyres, street submerged |
| 26 | [Flooding in Mumbai, India 2017.jpg](https://commons.wikimedia.org/wiki/File:Flooding_in_Mumbai,_India_2017.jpg) (Paasikivi) | CC BY-SA 4.0 | 1, 1, 1 | L1 | shallow standing water covering road, tyres mostly exposed |
| 29 | [Chennai-floods-2015-dec-3.jpg](https://commons.wikimedia.org/wiki/File:Chennai-floods-2015-dec-3.jpg) (Destination8infinity) | CC BY-SA 4.0 | 4, 4, 4 | L4 | Two yellow buses capsized, only roofs above muddy floodwater |
| 31 | [Chennai-floods-2015-dec-5.jpg](https://commons.wikimedia.org/wiki/File:Chennai-floods-2015-dec-5.jpg) (Destination8infinity) | CC BY-SA 4.0 | 4, 4, X | L4 | yellow vehicle roof only visible above brown floodwater |
| 34 | [BEST-NMMT-buses-CBD-Belapur-Rains.jpg](https://commons.wikimedia.org/wiki/File:BEST-NMMT-buses-CBD-Belapur-Rains.jpg) (Rsrikanth05) | CC BY-SA 4.0 | 0, 0, 0 | L0 | wet road reflections only tyres fully exposed no waterline |
| 35 | [Mumbai-rains.jpg](https://commons.wikimedia.org/wiki/File:Mumbai-rains.jpg) (Rakesh Krishna Kumar from Mumbai, India) | CC BY-SA 2.0 | X, 0, 0 | L0 | Wet road only, no water against tuk-tuk tyres |
| 36 | [Car after flood.jpg](https://commons.wikimedia.org/wiki/File:Car_after_flood.jpg) (Sreerag S J) | CC BY-SA 4.0 | 0, X, X | can't tell | readings disagree (0, None, None) |
| 42 | [2020 Hyderabad floods.jpg](https://commons.wikimedia.org/wiki/File:2020_Hyderabad_floods.jpg) (Strike Eagle) | CC BY-SA 4.0 | X, 2, X | can't tell | readings disagree (None, 2, None) |
