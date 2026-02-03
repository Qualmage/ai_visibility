Here is a detailed transcript of the video followed by a comprehensive report summarizing the discussion, technical details, and action items.

### **Part 1: Detailed Transcript**

**Speakers:**
*   **Speaker 1 (Rob):** Presenter, building the dashboard.
*   **Speaker 2 (Jason):** Supervisor/Reviewer, providing feedback.

**[00:00]**
**Rob:** So, I basically made sure we were keeping a bit more adherence to this original slide that Sarah mentioned. You know, the visibility score, citation sentiment, and all that. But what I also wanted to show was that...
**Jason:** And that chart... hold on... also that chart at the bottom.
**Rob:** This?
**Jason:** What she was... she really likes is that...
**Rob:** This one?
**Jason:** Yeah. Visibility by topic and the visibility by model.
**Rob:** Yeah. So what I've added so...
**Jason:** Not that... not that one in the left corner.
**Rob:** Visibility... this one?
**Jason:** Yeah.

**[00:51]**
**Rob:** Yeah, so the visibility score and the Share of Voice stuff, we would just look into the visibility score, right? And the way it's calculated...
**Jason:** That should be easy enough.
**Rob:** Yeah. You mentioned you wanted to use the mentions, right? So...
**Jason:** What? Sorry, say that again?
**Rob:** What you were saying in the email? You said... one second...
**Jason:** I want to change out... the... I forgot how my name comes up with my f***ing middle name. Um... I want to change around the prompts to make it more shopper-focused.
**Rob:** Yeah.

**[01:37]**
**Jason:** That's why I want to change out some of the dimension prompts for, you know, like price point with size. Like "85-inch TVs under $1,000."
**Rob:** Yeah.
**Jason:** Because pretty much everything is bringing up a prompt now. Or an AI response. It's crazy.
**Rob:** It is, yeah.
**Jason:** So that's why, like, and if you talk to Michael... that's why I don't think we need to go by prompts really. We can go by keyword volumes, and I think that's more accurate than what we get out of their platform because their keyword volumes are just honestly stupid.

**[02:18]**
**Rob:** Yeah, so the way they do the volumes is... yeah, this is the line I was talking about. It calculates using the number of brand mentions, position of the brand within each AI response, and the search volume of the topic.
**Jason:** Yeah, because they are using those volumes, it throws off the Share of Voice.
**Rob:** Yeah. It's a bit... and it's odd that if this weighting applies to ChatGPT... that's just a minor service compared to like AIOs (AI Overviews), right? So...
**Jason:** Yeah, I don't even know what that really means. "Search volume weighting only applies"... I mean they're only using it for ChatGPT?
**Rob:** Yeah.
**Jason:** It still doesn't matter because the volumes are so off.

**[03:03]**
**Rob:** Yeah, they are. And what we've got as well is... so if we brought in the Share of Voice by brand that we can calculate, sentiment distribution, and then also the... we've got mentions... we can get the mentions trend over time which is being brought in now. Obviously, this big jump is because we added the prompts in mid-Jan, right?
**Jason:** Yeah.
**Rob:** And then the topics... concepts, basically. It says "Topics by Mentions," but it is concepts by stats... sentiment.
**Jason:** Yeah, I don't mind calling them topics.
**Rob:** Yeah. But the thing to note is that there are two ways I found to get the prompts out, right? So there's the... if you go into the AI Visibility Overview and then we put in `samsung.com`...

**[04:08]**
**Jason:** Do you have to... or...
**Rob:** So if I was to go to US... all models... and then if we go to Cited Pages, we actually get all the Samsung... all the `samsung.com` domain... which we can then filter by US. Obviously, it's got like 292,000 here, but that gets whittled down to about 84,000 URLs. And if you go into, say, a US result, you can grab the prompts from their database... from their prompt volumes database. We can see a much wider range of prompts. And obviously, this is where the topic volumes are a joke, right? "How to stream a TV," 3.1 million topic volume, whatever that means.

**[05:13]**
**Rob:** But basically, we can get that kind of... we can get more prompts than the ones we've tracked to see how Samsung are performing and the other brands as well. It's just something to note.
**Jason:** Yeah, I think we want to keep this to TV though and away from the whole domain.
**Rob:** Yeah, so that's what I was saying is that we've got... one second, let me just show you this. *[Rob displays code editor/SQL query]* I would say... can we... how many US pages for the... using the filter for cited pages... I'll just show you this bit here. Just querying the database with all of it.

**[06:28]**
**Jason:** Before we go into all this stuff though... let's go with what we have.
**Rob:** Yeah, it's got TV there. So that's what I mean is that we've got all the URLs that are in the entire database outside of just the prompts that we tracked, if you wanted to incorporate some of that information.
**Jason:** And that's in the database in Claude that you guys put in? Or are you talking about the database in Semrush?
**Rob:** That's the Semrush database that we pulled, yeah.
**Jason:** Okay. Before we get into this stuff... cause there's... this UI is very unorganized. And there's a thousand ways to get stuff... which makes you question what we're looking at. So let's just look at the dashboard for now and where we're at in views.

**[07:27]**
**Jason:** I'm not saying you're wrong or anything, I just don't like how they've set up... I think this is... for the months they've had to put this together, I feel like they haven't been updating it since they essentially put it together and it shows. This is more of an initial take at what they are doing. But let's look at your dashboard of what you've created so far.

**[07:53]**
**Rob:** So this is a spin-off of this original dashboard that I had, right? Where we had the Share of Voice, Source Visibility, Referral Traffic, AI Visibility. And then I presented that last week, and then Sarah brought up this slide again. So I wanted to make sure we're laser-focused on what she wants and make sure it's aligned with this. Because otherwise, it's very easy for us to kind of deviate from the original plan. Use that as an MVP at least, and then we can start to maybe, if we wanted to deviate and add more features and insight, do that later. But for now, I just wanted to maybe align with you on making sure that... do we want to look at... review what these top-level KPIs are? And then some of the sections within... because this is quite busy, right?

**[09:05]**
**Jason:** Yeah, I understand. I understand what all this stuff is. So we added in... so one thing we want to look at, right, is the sources. It looks like you added some of the sources in?
**Rob:** Yeah, so we've got the sources by... we've got the competitor view. And then we've got the sources in terms of what media type—like Owned, Earned, Social—is quoting Samsung by two things: Mentions and Citations. And the difference between the two is that Mentions is when Samsung is mentioned in the body text, right? And then Citations is obviously the URL.
**Jason:** Yeah, yeah. I think it's easy to explain, don't worry about that. As much as... we need to have a breakdown of... by... not, I mean Owned, Earned, and Social benchmark competitors, that's fine. But we need to look at it more thematically, by topic.

**[10:25]**
**Rob:** Which was what I was starting to bring in here. So do you want me to... so this here... this was a renewed focus on looking at the sentiment distribution, looking at the new way of calculating Share of Voice to be more accurate, and also bringing in the concepts. So I was going to think, well, do we kind of want to roll in concepts in this... around here? So we talk about the high-level source breakdown by type, citations, mentions. We go into a bit more detail about the domains and the URLs themselves that are cited. And then somewhere down here we start to say, well, okay, we're going more granular to the point where we're now saying about themes and concepts. That kind of thing.

**[11:28]**
**Jason:** Yeah, we need to break down the sources thematically again, by topic.
**Rob:** Yeah, so what I found out though is that when you do go into Concepts... *[Navigates Semrush UI]* Let's grab this one. So let's say you're looking at "Picture Quality." It shows you the products, right?
**Jason:** Oh wow, yeah.
**Rob:** But to tie the URLs that are contributing to the "Picture Quality" concept in the prompts... they're not making it easy to... Like, what would be ideal is if you could click "Picture Quality" and then it brings up a new modal that says, "Here are the URLs that are being cited that are contributing to the picture quality concept."

**[12:50]**
**Jason:** Let's go to Sources.
**Rob:** Yeah, okay. And then...
**Jason:** And then we can filter on the Tags.
**Rob:** Okay, so you want... yeah.
**Jason:** And this is where our work came in. So you can type in like "4K" ... what she wants... and "OLED."
**Rob:** Okay, yeah. So if I was to select 4K...
**Jason:** And then...
**Rob:** Then here...
**Jason:** So it would be almost like we would show the Tags by...
**Rob:** ...the Tags by... *[Navigates to "Rankings"]* So here we have the Tags, we have the Mentions, Share of Voice, Visibility, Position. That seems like it's quite closely aligned. If we're saying Tags are Topics, that seems to me that it aligns well with the view that they want to see.

**[14:18]**
**Jason:** Yeah. So that's one thing, yeah, we knocked that out, right? That view. But then we want to do like a Sources view by Topic.
**Rob:** Okay, so if I went to Sources... yeah.
**Jason:** And then again we have our Tags.
**Rob:** Ah. *[Attempts to filter Tags on Sources tab]*
**Jason:** So I think you have to keep it on Domains. Because that's what we're looking for. And then you can break that down to like 4K or an OLED.
**Rob:** I see, yeah. Right, okay.
**Jason:** And that gives you... yeah. So that gives us the citation sources. So then we want to know who... because you gotta think of this through Taryn's lens, Rob. What is going to be... she wants to know who's doing well, right? Who's helping us get mentioned? And are they helping us get mentioned well?
**Rob:** In a positive or negative light. Yeah.

**[15:31]**
**Jason:** Yeah, to your point just there is that we also want to see negative because maybe that's somebody she wants to reach out to and say like, "Hey, what the f***?"
**Rob:** Got it. Right. So it's all about who's doing what for us. And who is talking about us. And what topics we are getting mentioned about the most. And who are those sources that are talking about us that are getting quoted in what topics they're using.
**Jason:** Okay.
**Rob:** So are Samsung in the conversation? Where are they being cited from? Which sources? And... what was the third one you were saying?
**Jason:** Mentions. And Sentiment. And I'd say Sentiment is actually even like a modifier, right, to citations and mentions. So that we know if this is good or bad.
**Rob:** Yeah.
**Jason:** So separating those two would be a good idea between good and bad.

**[19:15]**
**Rob:** Yeah, it's interesting actually... I'm not saying by every topic because you'll get... you'll have too many views.
**Jason:** Yeah.
**Rob:** Just giving like a high-level view of who's doing well for us. And maybe if you can create a table that can be sorted by that, that's malleable? I think that would be very valuable.
**Jason:** Okay. Yeah, cause I've noticed that they do generate these topics based on the prompts, right? So they group prompts into topics. It's basic clustering. But the way concepts are generated are different. So that was what I was trying to unpick. Because so long as there's a good representation of Topics to Sentiment, Citation/Mentions... stringing them together, that's what will help.

**[20:27]**
**Jason:** Can you go back to the Topic section?
**Rob:** Yeah.
**Jason:** I wonder if that's almost a misnomer to call it that. And it should be...
**Rob:** Ask Ed. Shoot an email to Ed and Brian to define the difference between Topics and Concepts.
**Jason:** Yeah, cause I'm not fully... I think when they look at their reviews, by the way, I think they kind of scrape from our prompts. So that's why I'm interested to see if we get more data once we start to modify the prompts.
**Rob:** Yeah. I'll find out... yeah I'll double-check the docs again just to make sure. And then...
**Jason:** No, ask Ed and Brian. Just go straight to them.
**Rob:** Yeah, I'll do that. Okay.
**Jason:** But get those views in and then send it over to me so I can look at it later today and see if I need to give you more feedback.
**Rob:** Got it. I'll get that on the go now and get that to you end of day. And send the clarifying email to Ed.
**Jason:** Yeah, cause let them clarify it for you. That's their job.
**Rob:** Yeah, good point. Awesome. All right. Thanks very much.
**Jason:** Bye guys.

***

### **Part 2: Meeting Report & Analysis**

**Date:** January 29, 2026
**Subject:** Samsung GEO Performance Dashboard - Refinement Strategy
**Attendees:** Rob (Lead/Dev), Jason (Supervisor)

#### **1. Executive Summary**
The meeting focused on refining the Samsung GEO (Generative Engine Optimization) Performance Dashboard. The current iteration is a functional MVP, but it requires specific adjustments to align with the client’s (Sarah/Taryn at Samsung) strategic goals. The objective is to move away from generic platform metrics and technical jargon, focusing instead on "Shopper-Centric" data.

The primary goal for the next iteration is to provide a "journey" view: **Who** (Sources) is talking about Samsung, regarding **What** (Topics like 4K/OLED), and with what **Sentiment**.

#### **2. Key Decisions & Requirements**

**A. Methodology Shift:**
*   **Prompt Strategy:** Shift from generic dimension prompts (e.g., "TV dimensions") to "Shopper-Focused" prompts (e.g., "85-inch TVs under $1000," "OLED reviews").
*   **Metric Reliability:** The team will ignore the platform’s (Semrush) native "Search Volume" and "Share of Voice" weighting calculations, deeming them inaccurate/ "stupid."
*   **Measurement Focus:** Success will be measured by **Raw Mentions** (text references) and **Citations** (linked sources), modified by **Sentiment** (Positive/Negative).

**B. Dashboard Architecture (The "Journey"):**
The dashboard needs to answer three specific questions for the client:
1.  **Who** is doing well for us? (Source Analysis)
2.  **What** are they talking about? (Thematic/Topic Analysis)
3.  **How** are they talking about us? (Sentiment Analysis)

**C. Specific View Requirements:**
*   **Source View by Topic:** A table or chart allowing the user to filter Sources (Domains) by Tags/Topics (e.g., filter by "4K" to see which websites are citing Samsung for 4K TVs).
*   **Sentiment Modifier:** Sentiment must be applied to both citations and mentions to highlight partners effectively helping the brand vs. those publishing negative content (potential outreach targets).

#### **3. Technical Details & Terminology**
*   **Platform:** Semrush (specifically the AI Visibility/GEO module) feeding into a custom dashboard (likely Looker/PowerBI).
*   **Tags vs. Topics vs. Concepts:**
    *   *Current State:* Confusion exists regarding the platform's distinction between "Topics" (basic clustering of prompts) and "Concepts" (sentiment-based stats).
    *   *Workaround:* The team will use **"Tags"** within the tool to filter domains. Rob confirmed that filtering Sources by Tags (e.g., "4K") aligns with the client's request.
*   **Filters:** "Owned," "Earned," and "Social" media types will be used, but the "Thematic" breakdown (4K, OLED, Picture Quality) is the priority.

#### **4. Action Items**

| Owner | Action Item | Priority |
| :--- | :--- | :--- |
| **Rob** | **Clarify Terminology:** Email Ed and Brian (Platform Reps) to explicitly define the difference between "Topics" and "Concepts" to ensure accurate reporting. | High |
| **Rob** | **Build Source Table:** Create a malleable/sortable table in the dashboard that displays **Sources (Domains)** filtered by **Tags (Topics)**. | High |
| **Rob** | **Sentiment Integration:** Ensure sentiment scores are visible alongside citations/mentions in the new view. | High |
| **Rob** | **Dashboard Delivery:** Send the updated dashboard view to Jason by EOD for feedback. | High |
| **Jason** | **Review:** Review the updated dashboard views later today. | Medium |