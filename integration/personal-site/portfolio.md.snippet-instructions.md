---
layout: page
title: Portfolio
permalink: /portfolio
published: true
---

<!-- SIDEBAR HTML -->
<div class="sidenav">
	<a href="#" class="navheader">Contents</a>
	<a href="#capstone-project"              >Capstone Project</a>
	<a href="#beavs-simulation"              >BEAVS Simulation</a>
	<a href="#esra-project-technical-report" >ESRA Project Technical Report</a>
	<a href="#public-obsidian-notes-repository" >Public Obsidian Notes Repository</a>
	<a href="#twincat-conveyor-problem"      >TwinCAT Conveyor Problem</a>
	<a href="#opens-lab-flodar-project-lead" >OPEnS Lab FloDar Project Lead</a>
	<a href="#first-robotics-team-experience">FIRST Robotics Team Experience</a>
	<a href="#ringgame"                      >RingGame</a>
	<a href="#chessdex"                      >ChessDex</a>
</div>

<!-- PAGE DESCRIPTION -->

*Here I go into (way too much) detail about projects I have been a part of or completed myself. This is the place where I get to talk as much as I like about what I like. It's not meant to be a short read or a quick summary. I try to keep things from being too excessive but, I'm not always successful. :)*

*If you have questions or want to learn more, please contact me at [dextercarpenter1@gmail.com](mailto:dextercarpenter1@gmail.com).*

<br>

<!-- PROJECTS BEGIN HERE -->

<hr>
# Capstone Project
*2023 - 2024*

To earn an engineering degree at Oregon State University (OSU), every student must complete a Capstone Project toward the end of their education. The purpose is to give students an opportunity to work in their dicipline on a team and contribute to a project that emulates what one might experience in industry. The project I chose took me down a slightly different path than most, as I ended up co-leading an experimental sounding rocket team.

<p align="center"><img src="/assets/images/ESRA_AIAA_logo_White.png" alt="ESRA_AIAA_logo" width="50%"></p>

## Context
But first, a small bit of history. OSU has a very large [AIAA chapter](https://osuaiaa.com/)<span class="tooltip"><sup>(?)</sup><span class="tooltiptext">American Institute of Aeronautics and Astronautics</span></span>
with over ten seperate teams doing rockets, planes, drones, and more. OSU has famously completed in and won the [SA Cup](https://www.soundingrocket.org/sa-cup-home.html)<span class="tooltip"><sup>(?)</sup><span class="tooltiptext">Spaceport America Cup</span></span>
hosted by [ESRA](https://www.soundingrocket.org/)<span class="tooltip"><sup>(?)</sup><span class="tooltiptext">Experimental Sounding Rocket Association</span></span>
in [2014](https://www.soundingrocket.org/2014-irec.html) and [2016](https://www.soundingrocket.org/2016-irec.html). However, with the COVID-19 pandemic and the passing of [Dr. Nancy Squires](https://osuaiaa.com/squires) many teams, including OSU's ESRA team, were discontinued. Myself and a good friend of mine were approached by the OSU AIAA President to revive the team as both of us had immense leadership experience with [FIRST Robotics](#first-robotics-team-experience). My friend was appointed as the Team Lead and I was selected to be the Treasurer since that role needed to be filled while still putting me in a leadership position. It was also beneficial since the work we did on the team would count for our Capstone.

<p align="center"><img src="/assets/images/MUESRAPicture.jpg" alt="MU_ESRA_Picture" width="80%"></p>

We agreed, recruited roughly five undergraduate (non-Capstone) students in the Fall, got accepted to the 2024 competition, and secured ourselves funding from the [OSGC](https://spacegrant.oregonstate.edu/) [UTEAP](https://spacegrant.oregonstate.edu/undergraduate-team-experience-award-program)<span class="tooltip"><sup>(?)</sup><span class="tooltiptext">Oregon Space Grant Consortium Undergraduate Team Experience Award Program</span></span>
 Grant. As I elaborate in [a later section](#esra-project-technical-report), I was the primary author for this grant as well as other technical documents. If you want to learn more about the grant, contact me. I don't have a section for it specifically.

## Category
<p><img class="floatright" src="/assets/images/ESRA_logo.png" alt="ESRA_logo" width="30%">
We made the decision in our application to compete in the 10,000ft SRAD<span class="tooltip"><sup>(?)</sup><span class="tooltiptext">Student Researched and Developed</span></span>
category. There are four categories. You can either aim for 10,000ft or 30,000ft. You're scored based on how closely you reach your target. Then you can either be an SRAD or a COTS<span class="tooltip"><sup>(?)</sup><span class="tooltiptext">Commercial Off-The-Shelf</span></span>
team. SRAD means you must create your own motor (propulsion system) and the freedom to put custom hardware elsewhere. In contrast, a COTS team must buy their motor from a commercial provider, and are slightly more limited as to what they could construct their rocket of. OSU has a history of mixing our own solid motors- in fact- OSU has one of the best-equipped motor mixing facilities in the US. While OSU has also previously competed in the 30k category, our team was brand new and very inexperienced. Thus the team made the decision to compete in the 10k SRAD category.
</p>

## Design
By Winter, we had recruited 3 additional Capstone students for a total of ~12 team members, and began designing our rocket. This term was painfully slow. The team was still getting to know one another and synchronous time commitments from everyone was a challenge. However, we were able to get through a majority of our design process. I want to go into detail about the rocket design, specifically the fins, nosecone, air brakes, and composites which are the portions that I contributed most to. However, in order to keep this more digestable, I've given it it's own seperate page.

# [Rocket Design Details →](/portfolio/rocket_design_details)

<p align="center"><img src="/assets/images/RamkoersCutaway.png" alt="RamkoersCutaway" width="100%"></p>

I will talk briefly about our air brake system, of which I wrote all of [the simulation](#beavs-simulation) and analysis required, and helped implement the control system. It was the biggest technical challenge and I contributed and considerable amount to it. We called it the *Blade Extending Apogee Variance System* (BEAVS) and you can read more about what I did specifically [in a later section](#beavs-simulation). The question arises *Why try and brake the rocket? Wouldn't you want to go as fast and high as possible?* and the answer is no. For the competition, you are scored based on how close to 10k ft you get. Whether you overshoot or undershoot, both deduct points. Most teams will attempt to engineer their rocket to a specific thrust curve, a specific mass, and specific mass distribution to achieve their target. However, this requires extremely meticulous design. Some teams such as ourselves, intentionally overshoot their target and engineer air brakes to activate at a specified altitude and duration to lower their apogee to their target. We took it a step further and used a [PID control system](https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller) to actuate the brakes.

<p align="center"><img src="/assets/images/BEAVS.png" alt="BEAVS" width="40%"><br><em>The physical BEAVS system</em></p>

## First Test Launch
By the end of the term in April we had a good idea of our design but, no progress on manufacturing the rocket. This was quite concerning as it put a lot of things to accomplish in the Spring before the competition in mid-June. With the proof of launch requirement rapidly approaching, myself and a few others put in 80-hour weeks to get the rocket constructed for our first test launch on April 28th. With a bit of luck, we had a successful launch and recovered the rocket with some minor damage (actual footage below).

<p align="center"><img src="/assets/images/BrothersLaunch480.gif" alt="BrothersLaunch" width="80%"></p>

We sustained some damage during our recovery. This is a single-deperation, dual-deploy rocket. I talk more about what this is in the [Rocket Design Details](/portfolio/rocket_design_details) but simply, we have two parachutes. A drogue, that deploys at <span class="tooltip">apogee<span class="tooltiptext">The highest point in the development of the rocket</span></span>, and a main, that deploys once the rocket passes ~1,500ft on descent. Our main parachute failed to deploy as the shock cord became tanged in the ejection charge wires. This caused the rocket to come down faster than desired, and caused damage to the upper section of the body tube, just below the nosecone, shown below.

<p align="center"><img src="/assets/images/BrothersDamage.jpg" alt="BrothersDamage" width="80%"></p>

The initial solution was simple. Cut the cracked portion away. We cut about 14" off with only one small problem. However, this complicates things. Our rocket lost a lot of stability by reucing its overall length. Rocket stability can be simplified to the distance between the [center of pressure](https://en.wikipedia.org/wiki/Center_of_pressure_(fluid_mechanics)) (C<sub>p</sub>) and the [center of mass](https://en.wikipedia.org/wiki/Center_of_mass) (C<sub>g</sub>). A stable rocket has a center of pressure *below* the center of mass. [NASA](https://www.grc.nasa.gov/www/k-12/VirtualAero/BottleRocket/airplane/rktstab.html) has a convient graphic to help illustrate this.

<p align="center"><a href="https://www.grc.nasa.gov/www/k-12/VirtualAero/BottleRocket/airplane/rktstab.html"><img src="/assets/images/rktstab.gif" alt="rktstab" width="80%"></a></p>

The damage lowered our C<sub>g</sub> closer to our C<sub>p</sub>, worsening stability. To solve this issue, we had to either reduce the mass on the lower half of the rocket (not feasible) or lower our C<sub>p</sub>. Lowering the C<sub>p</sub> can be done by increasing the fin size. Since the fins were already cured onto the airframe by a very labor intensive and complicated process that I talk about in the [Rocket Design Details](/portfolio/rocket_design_details), it was not so simple to make the fins bigger. We had the idea of adding what we eventually called 'strakes,' some long and short fins that wouldn't be susceptable to [fin flutter](https://en.wikipedia.org/wiki/Aeroelasticity#Flutter), wouldn't require a carbon fiber layup, and wouldn't disrupt the flow over the original set of fins. In simulating the idea, we found that there were some geometries of the strakes that were very stable and very unstable. We realized we had to be very careful when choosing the geometry as to not pick one that would cause instability. An ideal course of action would have been to perform either [Computational Fluid Dynamics](https://en.wikipedia.org/wiki/Computational_fluid_dynamics) or an experiment in a wind tunnel with a scale model. Then, test our design on a sub-scale rocket. However, we didn't have time for any of these solutions. We talked to several professors at OSU and our mentors which gave enough insight to make the decision to proceed with our idea. We noticed that there appeared to be periodic critical lengths of the strakes that would cause tubulent flow across the fins (bad). We settled upon a geometry that sat in between the points and hoped for the best.

<p align="center"><img src="/assets/images/strakes.png" alt="strakes" width="80%"></p>

## Spaceport America
Soon the competition arrived, our team drove from Corvallis, OR to Las Cruces, NM where we stayed for the week-long competition. After 3 days of poor weather conditions, some integration problems, and delays from the event organizers, we finally were able to get off the ground!

<p align="center">
	<img src="/assets/images/OnTheRail.jpg" alt="OnTheRail" height="330"> 
	<img src="/assets/images/OffTheRail.jpg" alt="OffTheRail" height="330"> 
	<img src="/assets/images/InFlight.jpg" alt="InFlight" height="330">
</p>

Unfortunately, our flight didn't go as well we hoped. Our custom motor casing failed mid-flight and our motor lost thrust prematurely. However, it became significantly worse when our ejection charges failed to seperate our rocket, sending our rocket down ballistic. This was a rookie mistake and easily avoidable. Granted, we were a rookie team and were impressed with ourselves for getting as far as we did. Myself and the few others who graduated from the team felt extremely accomplished as we had laid the foundation for the team to continue to operate in years to come. The team this year was untraditionally almost entirely non-Capstone students. Only 4 of the 12 members attending the competition were seniors. Traditionally, the team is comprised of almost exclusively Capstone seniors. However, my colleagues and I intentionally laid the groundwork to enable the team to govern themselves, something we all belived to be very valuable. 

<p align="center"><img src="/assets/images/LaunchRailShot.jpg" alt="LaunchRailShot" width="80%"></p>

Here is a fun recap video made by one of my teammates, [Cody Eutsler](https://www.linkedin.com/in/cody-eutsler-62b792299/).

<p align="center">
<iframe width="560" height="315" src="https://www.youtube.com/embed/e0LpQ6RYETU?si=mVS7pFPLhDm0PAza" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</p>

<hr>
# [BEAVS Simulation](https://github.com/DexterCarpenter/BEAVS4-Simulation)
*2024*

This project involed writing a simulation in [MATLAB](https://www.mathworks.com/products/matlab.html) for the [OSU ESRA Team](#capstone-project) (see above). The simulation is used to gain understanding of how the *Blade Extending Apogee Variance System* (BEAVS) will affect the rocket's flight path. The simulation takes [OpenRocket](https://openrocket.info/) data export in conjunction with [OpenMotor](https://github.com/reilleya/openMotor) custom motors as a basis. The project is hosted on my [GitHub](https://github.com/DexterCarpenter/BEAVS4-Simulation).

<p align="center"><img src="/assets/images/BEAVS.png" alt="BEAVS" width="40%"><br><em>The physical BEAVS system</em></p>

### Objectives
- Understand the total braking power of BEAVS given varying rocket designs
- Separation failure risk analysis
- PID control simulation
- Output data to BEAVS hardware to simulate flight (did not achieve)

The first objective was to understand the total braking power of BEAVS given varying rocket designs. Early in the development process the propulsion team needed to determine how large to make the rocket motor. To determine this, the team needed to understand how much BEAVS could theoretically reduce the apogee by. This was a very large first leap. To achieve this, the aerodynamic drag problem must be solved, a process for importing simulated rocket flight data into MATLAB must be written, and a solution to calculate how BEAVS’s change to the drag will affect the flight. All these problems are solved with the Control Range Graphic shown below.

<p align="center"><img src="/assets/images/ControlRangeGraphic.png" alt="ControlRangeGraphic"></p>

This graphic highlights the minimum and maximum BEAVS could lower the apogee by. The solid blue line represents the rocket’s altitude over time if no air braking occurs. This is equivalent to the direct data import from OpenRocket. The dashed blue line represents a maximum braking scenario and can be interpreted as the most that BEAVS could brake, if needed. The orange lines show the total coefficient of drag of the entire rocket over time.

Due to the location of BEAVS being on the lower (aft) section of the rocket, there is a high risk of separation failure. Separation failure occurs when the lower section has more drag than the forward section such that it causes the two sections to separate before it reaches apogee. This would be catastrophic for the competition. To mediate this failure mode, the MATLAB simulation calculates the force exerted by BEAVS and the force felt at the coupler between the two sections. This is represented in the following figure.

<p align="center"><img src="/assets/images/ForcesDuringCoast.png" alt="ForcesDuringCoast"></p>

Due to the difficulty of testing BEAVS, it was required that the MATLAB simulation also implements a [PID control system](https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller). The simulation was written initially with this functionality in mind. The simulation takes an input for the blade extension and calculates the force of drag it will induce. The system is iteratively solved using [Forward Euler](https://en.wikipedia.org/wiki/Euler_method). At each time step, the PID function compares the current velocity to a target velocity using a height to velocity lookup table. Then outputs a desired blade extension amount. This desired blade extension amount is then fed to another function that evaluates whether the blades can be adjusted to the desired position. If possible, give a constant blade extension/retraction rate, the blade extension is set to the desired position. If the desired position is unreachable in the time step, it extends the most it could in the time step and returns that position to the Forward Euler iterator. Using this, K<sub>p</sub>, K<sub>i</sub>, and K<sub>d</sub> values can be found with manual tuning. The following figure shows the error in velocities over time given a sample initial data set.

<p align="center"><img src="/assets/images/PIDGraphic.png" alt="PIDGraphic"></p>

<hr>
# [ESRA Project Technical Report](https://www.dropbox.com/scl/fo/1esn53zry4i2fjv8t0i5m/ABTbk8A2A9bhiVj74qt7v-0?dl=0&e=1&preview=Team_68_Technical_Report_2024_Spaceport_America_Cup.pdf&rlkey=chkbse71359m5jrlwx5wczgy6&st=6go4n431)
*2024*

As part of my work on [OSU ESRA](#capstone-project) (see above), I was the primary author of the Project Technical Report for our team. I orchestrated the entirety of the report, writing a prodominant portion and delegating the remainder of sections to my fellow team members. The report "overviews their project for the judging
panel and other competition officials" and therefore provides a fully comprehensive document of the entire project. It is worth 20% of the final score for the competition.

Our team's Technical Report placed **29th** out of 121 teams, scoring **183.7** of the **200** possible points. This is verifiable with the Final Scores on [soundingrocket.org](https://www.soundingrocket.org/2024-sa-cup.html).

<p align="center"><embed src="/assets/pdfs/Team_68_Project_Technical_Report_to_the_2024_Spaceport_America_Cup.pdf"
	width="80%" height="600" type="application/pdf"></p>

<hr>
# [Public Obsidian Notes Repository](https://github.com/DexterCarpenter/ObsidianGitVault.Public)
*2025*

I started using [Obsidian](https://obsidian.md/) for taking both personal and work-related notes. I began to really enjoy it, especially the integration with git and auto-committing. However, since I use it for work the repository needs to be private as to not be in violation of any potential NDAs. This quickly became irritating as I found myself frequently wanting to share notes I take with coworkers and friends. Often times I'd find a dumb fix to an issue and I like to document briefly in a note what I did to get things to work- both for my future self and anyone else who comes across the same problem.

So, I did a little research and found that [GitHub Actions](https://github.com/features/actions) is fully capable of creating an automation that splits a specific section of my private repository and commits it to a public-facing repository without exposing anything extraneous. With a day's work of development I now have a publicly-facing repository that automatically updates with notes I select as public.

You can read the documentation on how to set it up for yourself in the [README of my Public Repo](https://github.com/DexterCarpenter/ObsidianGitVault.Public).

<hr>
# [TwinCAT Conveyor Problem](https://github.com/DexterCarpenter/TwinCATConveyorProblem)
*2024*

This was a 2-day project in which I learned [Beckhoff's TwinCAT 3 XAE](https://www.beckhoff.com/en-us/support/download-finder/search-result/?download_group=97028248) and created a hypothetical solution to a problem for a job interview. I had no prior experience with Structured Text or Pascal prior to this!

### Objectives
- We have an conveyor with 4 buttons Start Stop AND E-Stop AND Reset.
- When system starts it shouldnt do anything until reset.
- Starting it should speed up to a RUN_SPEED, over ACCEL_TIME and maintain.
- If stop is Pressed speed should decrease to 0 over DECCEL_TIME.
- If E_Stop is Pressed speed should go immediately to 0.
- Before resuming operation after E-Stop, the system should require a reset.

<p align="center">
<iframe width="560" height="315" src="https://www.youtube.com/embed/GMHNJdMj_Cc?si=u64iGnNKQQkcnuwt" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</p>

<hr>
# [OPEnS Lab *FloDar* Project Lead](https://github.com/OPEnSLab-OSU/OPEnS-Lab-Home/wiki/FloDar)
*Jan 2021 - Oct 2022*

At Oregon State University’s [Openly Published Environmental Sensing Lab](https://open-sensing.org/) (OPEnS Lab), I contributed to the development and deployment of [FloDar](https://github.com/OPEnSLab-OSU/OPEnS-Lab-Home/wiki/FloDar), a low-cost sensing system designed to monitor groundwater discharge and its properties. This project, conducted in collaboration with the Oregon Department of Transportation and the Oregon State College of Forestry, addresses the need for quantitative data on groundwater removal systems, which are crucial for landslide mitigation and infrastructure safety.

<p align="center"><img src="/assets/images/FloDar.png" alt="FloDar"></p>

## Responsibilities and Contributions
- *Maintaining GitHub Repository:* I ensured that our [GitHub repository](https://github.com/OPEnSLab-OSU/FloDar) was consistently updated with the latest documentation, code, schematics, and images. This was vital for open-source collaboration and maintaining transparency with stakeholders.
- *Facilitating Communication:* I played a key role in fostering effective communication with stakeholders and lab management. This included regular updates, clarifying project goals, and ensuring that all team members were aligned with the project’s objectives.
- *Meeting Preparation and Coordination:* I organized and prepared for group meetings, including drafting weekly reports, updating project timelines, and gathering relevant data. I also coordinated schedules for field deployments and build parties, ensuring smooth logistical operations.
- *Project Management:* I maintained the project checklist and timeline, keeping track of milestones and deadlines. I went out of my way to do research and find a project management software to help myself stay organized. I was able to monitor tasks and update a Gantt Chart.

## Technical Achievements
FloDar was successfully installed at three hillside locations, with plans for expansion. The system measures flow rate, turbidity, and temperature at specified intervals, capable of handling over 700L/min with an uncertainty of ±7L/min. This system provides critical data for understanding groundwater dynamics and improving the maintenance and operation of drainage systems.

Through my work at OPEnS Lab, I gained valuable experience in project management, team coordination, and environmental sensing technology, all of which have deepened my understanding of engineering solutions for real-world problems.

<hr>
# FIRST Robotics Team Experience
*2016 - 2019*

In high school, I became chronically involved with the [FIRST® Robotics Competition](https://www.firstinspires.org/robotics/frc) (FRC) team. Each year FRC teams design, program, and build a robot from scratch and common set of rules to play in a themed head-to-head challenge. This was the beginning of my career in engineering and has taught me more about engineering and leadership than anything else. I still am friends with many of my teamates to this day. A few things that set our team aside from many others are being student lead, meaning the students were in charge of making the decisions and our mentors were a hands-off resource. We also had significantly less team members and funding, which provided an additional barrier to our success.

For the rest of this section, I'll talk through what I did each year, sharing my story. I'll then end with a more technical description of our 2019 robot *Scorpion*.

<p align="center"><img src="/assets/images/PigmiceLogo.webp" alt="Pigmice Logo" width="40%"></p>

## Freshman Year: Joining the Team
I joined [our FRC team](https://www.pigmice.com/) as a freshman, eager to immerse myself in the world of engineering and robotics. This initial year provided a foundation in teamwork, basic mechanical concepts, and the excitement of competitive robotics. Our robot did adequately this year, but our team had a very laid-back approach to the competition.

## Sophomore Year: Build Lead
In my sophomore year, I was appointed as the Build Lead. Under the mentorship of the Manufacturing Captain, I got my first glimpse into leadership and hands-on engineering. Our department was responsible for transforming designs from the Design Department into functional components for our robot. We began prototyping with wood and cardboard, allowing for quick iterations and testing. Once designs were more developed, we manufactured the final parts using aluminum. My primary contribution to the team was the 'Shooter.' This was a flywheel mechanism that launched wiffle balls roughly 15ft into the air to score them. Our team performed very poorly this year. At each of our competitions, we struggled to field a functional robot.

## Junior Year: Co-Leading as Manufacturing Captain
My junior year marked a significant step forward as I was elected to co-lead as the Manufacturing Captain. This role intensified my responsibilities and honed my skills in organization, communication, and managing a team under stressful environments. The challenge this year required a milk crate-sized cube to be placed on a scale +8ft into the air. Our team decided on using an 'elevator' mechanism, but were split on two different methods. We decided to work on both solutions in parallel. This ended up being a valueable lesson in both team dynamics and engineering. Our hard work and improved processes paid off, as we advanced to the District Championships for the first time in many years. This achievement was a testament to our improved design, iteration, and testing methods. The new set of leadership, including myself, had taken a vastly different approach to the team and after tasting success, were eager to do even better next year.

<p align="center"><img src="/assets/images/OtisDCMP1.jpg" alt="Otis" width="80%"></p>

## Senior Year: Team Captain
In my senior year, I was honored to be elected as the Team Captain, co-leading the entire team. My focus on leadership, organization, and fostering effective communication among team members culminated in an exceptional season. We advanced to the World-level competition in Houston, TX, where we became finalists in the playoffs of our division. Our team’s journey ended only after a closely contested match with the eventual world champions.

<p align="center"><img src="/assets/images/PigmiceHouston.JPG" alt="Celebrating getting to finals" width="80%"></p>

Throughout my journey with the FRC team, I developed a strong foundation in engineering principles, leadership, and teamwork. These experiences have significantly shaped my approach to problem-solving and project management, skills that I continue to apply in my ongoing engineering endeavors.

# [Scorpion Design Details →](/portfolio/scorpion_design_details)

<p align="center"><img src="/assets/images/scorpion.webp" alt="Scorpion" width="60%"></p>

<hr>
# [RingGame](https://github.com/DexterCarpenter/RingGame)
*2020*

An Arduino-based arcade style game. Press the button when the lights line up to proceed to a faster level. 

This was a one-day project. Using an [Adafruit Neopixel ring (24)](https://www.adafruit.com/product/1586), an [Arduinio Uno](https://store.arduino.cc/products/arduino-uno-rev3), and a button I created a game where the objective is to press the button when the "runner" and the "selector" are aligned. If you are successful, you get a green flash and the runner gets faster. This proceeds until you miss, in which an animation plays and restarts the runner's speed.

My goal was to make this as simple as possible, using just the NeoPixel and a button as the UI.

<p align="center"><img src="/assets/images/RingGame.gif" alt="RingGame"></p>

<hr>
# ChessDex
*2024 – present*

A chess engine and bitboard library written from scratch in Python, with a browser play UI. You can [play against the engine live](/chessdex/) on this site or browse the [ChessDex repository](https://github.com/DexterCarpenter/ChessDex).
