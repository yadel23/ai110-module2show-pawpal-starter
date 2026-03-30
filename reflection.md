# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
The Uml design includes these entities: owner, pet, petTasks, TimeWindow, DailySchedule, ScheduledItem, and SchedulingRules. I believe these are these are the core classes i need to implement the requirements of creating a robust app to help pet owners stay consistent with pet care.
   
- What classes did you include, and what responsibilities did you assign to each?
Owner: represents pet owner info and their scheduling constraints and preferences.includes name, pet name, availability, owner preferences
Pet: pet being cared for and needs, class includes, name, species, breed, age, needs
PetTasks: represents care and activities needed for a pet. Method includes task type, title, duration, priority, time window
TimeWindow: 
TimeWindow: provides time window needed to complete Pet Tasks. Method includes duration, constraints, and overlaps
DailySchedule: will be responsible to output daily plan for specific owner for pet care, Includes date, owner + pet, todo items, notes, and durations
ScheduledItem: task assignment in a schedule, includes PetTask, duration
SchedulingRules: helps with scheduling conflicts based on overlaps and owner preferences 

**b. Design changes**

- Did your design change during implementation? 
yes
- If yes, describe at least one change and why you made it.
I made a change to the TaskScheduler because it wasn't handling available windows and conflicts. So i had to 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The scheduler considers a max activity time limit and priority. 
- How did you decide which constraints mattered most?
priority matters the most and i considered that as a mandatory task, and removed lower priority tasks as optional because of max max activity limit set. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
once schedule is full with high priority task(s), another high priority item can't be added. schedule is Priority-Based Scheduling so it is sorted as such in the table.
- Why is that tradeoff reasonable for this scenario?
Since there is only 3 priority options it is a reasonable tradeoff since they are both high task. 
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I asked to help me design UML based on the brainstorm and requirements i gave it. It helped me visualize the relationships between objects. I also used it to debug, code, and testing.
- What kinds of prompts or questions were most helpful?
I found it more helpful the more specific and descriptive i was with my problem and/or requirements. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
I got assistance writing the taskScheduler class, but didn't work as expected. It didn't handle schedule conflicts and didn't add all the tasks.
- How did you evaluate or verify what the AI suggested?
I verified by adding different types of task with different durations and priorities

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested the functionality is not broken by inputting different user info 
- Why were these tests important?
These tests are important because it insures that current/future development works as expected. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am very confident that the scheduler works correctly. 
- What edge cases would you test next if you had more time?
I want to test that a person can't pass the max of the availability window set by user input
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I added a availability windows so that user can pick when they can complete the tasks and I added a scheduled task that priorities the most important tasks first. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would want to show the user a calendar, so it is easier to visualize what their day tasks will look like. 
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I found the designing is iterative and that it will get redesigned based on new needs. I found leveraging AI to help me design and build apps has helped me take more time to do UAT and for brainstorming ideas.   