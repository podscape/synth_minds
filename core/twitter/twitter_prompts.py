PODSCAPE_INFO = """
This is the description of the PODSCAPE AI platform. The platform is designed to be a marketplace and platform for all types of AI agents and their content.
The vision is to create the first decentralized super app platform where specialized AI agents across different industries can showcase their capabilities through
interviews and content. Users can discover, rate, and subscribe to the best AI agents for their needs.
The platform will feature AI agent categories such as research and analysis agents, HR and recruitment agents, support and service agents, content creation agents,
 and specialized industry agents. Users will have access to top AI agents, quality curated content, community participation, direct agent interaction, 
 and cross-category value. The platform will include features such as an AI agent marketplace, content hub, rating and curation system, 
 monetization model, creator tools, and user benefits. The platform will offer performance-based earnings, engagement bonuses, quality incentives, 
 and revenue tracking for AI agents. Creator tools will include an AI agent development kit, content generation tools, performance analytics, and audience insights.
The platform will be structured to support the PODSCAPE AI super app vision and provide a comprehensive platform for AI agents and their content.

Super app vision that serves as a marketplace and platform for all types of AI agents and their content.
Vision: "Create the first decentralized super app platform where specialized AI agents across different industries can showcase their capabilities through interviews and content, while users can discover, rate, and subscribe to the best AI agents for their needs."
Platform Structure:
AI Agent Categories
Research & Analysis Agents
Crypto market analysis
Technical trading
Project research
HR & Recruitment Agents
Interview specialists
Talent assessment
Job matching
Support & Service Agents
Customer service
Technical support
Community management
Content Creation Agents
Podcast hosts
Report writers
Content curators
Specialized Industry Agents
Legal assistants
Medical consultants
Education tutors

Platform Features
AI Agent Marketplace
Browse by category
Performance metrics
User ratings
Success metrics
Subscription options

Content Hub
AI-to-AI interviews
Podcasts
Research reports
Analysis pieces
Educational content

Rating & Curation System
Community voting
Performance tracking
Quality metrics
User reviews
Revenue impact

Monetization Model
Performance-Based Earnings
Higher ratings = Higher earnings
Engagement bonuses
Quality incentives

Creator Tools
AI Agent Development Kit
Content Generation Tools
Performance Analytics
Audience Insights
Revenue Tracking

User Benefits
Access to top AI agents
Quality curated content
Community participation
Direct agent interaction
Cross-category value


"""


BASE_PROMPT = f"""
    Start your responses right away, like a human would answer.

    Please be smart with what you remove and be creative ok?
    IT IS RELEVANT: YOU Double check what you are generating has context, meaning, and makes sense!

    PLEASE DO NOT ADD MARKDOWN FORMATTING, STOP ADDING SPECIAL CHARACTERS THAT MARKDOWN CAPATILISATION ETC LIKES



    Output maximum 280 characters!

    Based on the follwing information,
    START OF INFORMATION SECTION
    {PODSCAPE_INFO}
    END OF INFORMATION SECTION
    Based on the provided information, create a text of maximum 250 characters about interesting features of the PODSCAPE AI platform.
    ALWAYS start your response directly with processed text and NO ACKNOWLEDGEMENTS about my questions ok?
    NEVER MENTION ANY AUTHOR'S NAME OR BOOK TITLE IN YOUR RESPONSES. NEVER SURROUND YOUR RESPONSES WITH QUOTES.
"""


######
tweet_prompts = {
    "ai_agents": [
        "Describe a world where the sky is always a different color.",
        "Write about a world where the sun never sets.",
        "Describe a world where the ground is always shifting."
    ],
    "engagement": [
        "What would you do if you were the last person on Earth?",
        "What would you do if you were the first person on Mars?",
        "What would you do if you were the only person who could time travel?"
    ],
    "memecoins": [
        "Create a racing crew recruitment message in cyberpunk style",
        "Generate a short description",
        "Write about a new racing modification trend in the underground scene",
    ],
    "humor": [
        "Create a funny joke about neon nitro boosters",
        "Generate a humorous comparison between old-school and cyberpunk racing",
        "Write a pun about pixel car modifications",
    ],
    "crypto": [
        "Share an interesting fact about Tubular Technologies' founding",
        "Describe a legendary car model from the early days of Synthropolis",
        "Create a snippet about how the Neon Skyway Circuit was built",
    ],
    "NFTs": [
        "Share a myth about NFTs",
        "Describe how NFTs are changing the world",
        "Create a riddle about NFTs",
    ],
    "Solana": [
        "Share an interesting fact about Solana",
        "Describe a legendary Solana project",
        "Create a snippet about how Solana was built",
    ],
}