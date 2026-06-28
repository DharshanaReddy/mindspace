"""
Mental health knowledge base for RAG-powered chatbot (Kai).
Evidence-based resources seeded into ChromaDB for semantic retrieval.
"""

MENTAL_HEALTH_DOCUMENTS = [
    {
        "id": "cbt-techniques-001",
        "content": """Cognitive Behavioral Therapy (CBT) core techniques:
        Thought records: Write down the situation, automatic thought, emotion, evidence for/against the thought, and a balanced perspective.
        Behavioral activation: When depressed, schedule small pleasurable activities to break the inactivity cycle.
        Cognitive restructuring: Challenge distorted thoughts by asking "What evidence do I have?", "What would I tell a friend?", "What's the most realistic outcome?"
        Exposure: Gradually face feared situations in a safe, controlled way to reduce anxiety.
        CBT is evidence-based and shown effective for depression, anxiety, PTSD, OCD, and eating disorders.""",
        "metadata": {"category": "therapy", "type": "cbt"},
    },
    {
        "id": "grounding-techniques-001",
        "content": """Grounding techniques for anxiety and dissociation:
        5-4-3-2-1 technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.
        Box breathing: Inhale 4 counts, hold 4, exhale 4, hold 4. Repeat 4 times.
        4-7-8 breathing: Inhale 4 counts, hold 7, exhale 8. Activates parasympathetic nervous system.
        Cold water: Splashing cold water on face triggers the dive reflex, slowing heart rate.
        Physical grounding: Press feet firmly into floor, describe your surroundings in detail.
        Ice cube: Hold an ice cube — the physical sensation interrupts panic cycles.
        These techniques work by redirecting attention from anxious thoughts to present sensory experience.""",
        "metadata": {"category": "techniques", "type": "grounding"},
    },
    {
        "id": "depression-support-001",
        "content": """Supporting someone (or yourself) through depression:
        Depression is not weakness or laziness — it is a medical condition affecting brain chemistry.
        Behavioral activation: Even 5-10 minutes of activity can break the cycle of inactivity.
        Social connection: Isolation worsens depression; even small interactions help.
        Sleep hygiene: Consistent sleep/wake times stabilize mood regulation.
        Nutrition: Omega-3 fatty acids, B vitamins, and gut health influence mood.
        Exercise: 30 minutes of moderate exercise 3x/week is as effective as antidepressants for mild-moderate depression.
        Professional help: If symptoms persist 2+ weeks or interfere with daily life, speak to a mental health professional.
        Medications: Antidepressants are effective and not addictive — stigma around them is unfounded.""",
        "metadata": {"category": "condition", "type": "depression"},
    },
    {
        "id": "anxiety-management-001",
        "content": """Anxiety management strategies:
        Anxiety is a normal response to perceived threat — it becomes problematic when disproportionate.
        Worry time: Schedule 15 minutes daily to think about worries. Outside that time, postpone worry.
        Acceptance: Try to accept uncertainty rather than seeking reassurance, which reinforces anxiety.
        Progressive muscle relaxation: Systematically tense and release muscle groups from feet to face.
        Mindfulness: Observe anxious thoughts as 'just thoughts', not facts: 'I notice I'm having the thought that...'
        Limit caffeine and alcohol: Both significantly worsen anxiety.
        Exercise is one of the most effective anxiolytic interventions available.
        Journaling: Writing down worries reduces their power and provides cognitive distance.""",
        "metadata": {"category": "condition", "type": "anxiety"},
    },
    {
        "id": "crisis-resources-001",
        "content": """Crisis resources and when to seek immediate help:
        988 Suicide & Crisis Lifeline (US): Call or text 988 — available 24/7, free and confidential.
        Crisis Text Line: Text HOME to 741741 from anywhere in the US.
        International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/
        Signs you need immediate help: thoughts of suicide or self-harm, inability to care for yourself, psychosis.
        Emergency: Call 911 or go to the nearest emergency room if you or someone is in immediate danger.
        Remember: Seeking help is a sign of strength, not weakness.
        You do not need to be 'bad enough' to deserve support — reach out early.""",
        "metadata": {"category": "crisis", "type": "resources"},
    },
    {
        "id": "self-compassion-001",
        "content": """Self-compassion practices (Dr. Kristin Neff framework):
        Three components: Self-kindness (vs self-judgment), Common humanity (vs isolation), Mindfulness (vs over-identification).
        Self-kindness: Speak to yourself as you would speak to a good friend who is struggling.
        Common humanity: Suffering and imperfection are part of the shared human experience — you are not alone.
        Mindfulness: Acknowledge painful feelings without suppressing or exaggerating them.
        Practice: Place hand on heart, breathe, say 'This is a moment of suffering. Suffering is part of life. May I be kind to myself.'
        Research shows self-compassion is strongly linked to emotional resilience, lower anxiety, and higher wellbeing.
        Self-compassion is NOT self-pity or lowered standards — it actually improves motivation.""",
        "metadata": {"category": "techniques", "type": "self-compassion"},
    },
    {
        "id": "sleep-mental-health-001",
        "content": """Sleep and mental health connection:
        Poor sleep is both a symptom and cause of depression and anxiety — addressing sleep can break this cycle.
        Sleep hygiene fundamentals: Consistent sleep/wake times, dark and cool room (65-68°F), no screens 1 hour before bed.
        Caffeine has a half-life of 5-6 hours — avoid after 2pm if sleep is an issue.
        Sleep restriction therapy: Temporarily limit time in bed to build sleep drive — counterintuitive but effective.
        Cognitive arousal at bedtime: Write a to-do list for tomorrow to 'offload' worries from your mind.
        If you can't sleep after 20 minutes: Leave bed, do a quiet activity, return when sleepy.
        Napping: Limit to 20-30 minutes before 3pm to avoid disrupting nighttime sleep.""",
        "metadata": {"category": "wellness", "type": "sleep"},
    },
    {
        "id": "loneliness-connection-001",
        "content": """Addressing loneliness and building connection:
        Loneliness is a signal, like hunger — it tells you that you need connection.
        Chronic loneliness has health impacts equivalent to smoking 15 cigarettes per day.
        Quality over quantity: One deep connection is more protective than many superficial ones.
        Start small: Brief exchanges with strangers (barista, neighbor) reduce loneliness surprisingly effectively.
        Online communities: Can provide genuine connection, especially for niche interests or identities.
        Volunteering: Reduces loneliness by providing purpose and regular social contact.
        Pets: Provide real social bonding and reduce cortisol levels.
        Self-disclosure: Gradually sharing more personal information deepens relationships.
        Vulnerability is the birthplace of connection — authenticity attracts authentic people.""",
        "metadata": {"category": "condition", "type": "loneliness"},
    },
    {
        "id": "stress-burnout-001",
        "content": """Stress and burnout recovery:
        Burnout is a state of chronic workplace stress characterized by exhaustion, cynicism, and reduced efficacy.
        Recovery requires genuine rest: not just sleep, but creative, social, and physical rest too.
        Boundaries: Learn to say no without over-explaining. 'I can't take that on right now' is a complete sentence.
        Micro-recoveries: 5-minute breaks every 90 minutes are more restorative than one long break.
        Values clarification: Burnout often signals misalignment between work and personal values.
        Autonomy and control are the strongest predictors of burnout prevention.
        Nature exposure for 20-30 minutes significantly reduces cortisol and adrenaline levels.
        Burnout recovery timeline: typically 3-6 months of intentional recovery — be patient.""",
        "metadata": {"category": "condition", "type": "burnout"},
    },
    {
        "id": "mindfulness-basics-001",
        "content": """Mindfulness fundamentals and practice:
        Mindfulness is paying attention to the present moment, non-judgmentally.
        Research shows 8 weeks of mindfulness practice produces measurable changes in brain structure.
        Beginner practice: 5 minutes of breath awareness daily. Notice breath, mind wanders, gently return.
        RAIN technique: Recognize, Allow, Investigate (with curiosity), Nurture (with self-compassion).
        Informal mindfulness: Bring full attention to routine activities — eating, walking, showering.
        Apps: Headspace, Calm, Insight Timer, Waking Up — all evidence-based guided programs.
        Mindfulness does NOT mean emptying the mind — it means noticing when the mind wanders and returning.
        Regular practice builds the 'muscle' of attention and reduces default mode network rumination.""",
        "metadata": {"category": "techniques", "type": "mindfulness"},
    },
    {
        "id": "ptsd-trauma-001",
        "content": """PTSD and trauma: understanding and healing approaches:
        Trauma is not weakness — it is a normal nervous system response to abnormal experiences.
        PTSD symptoms: intrusive memories/flashbacks, avoidance, negative mood changes, hypervigilance.
        Not everyone exposed to trauma develops PTSD; social support is the strongest protective factor.
        Evidence-based treatments: EMDR (Eye Movement Desensitization and Reprocessing), CPT (Cognitive Processing Therapy), Prolonged Exposure.
        Trauma-informed grounding: when triggered, orient to safety — name the room, feel the chair, say the date aloud.
        The window of tolerance: a state between hyperarousal (panic) and hypoarousal (shutdown) where healing happens.
        Somatic approaches: trauma is stored in the body — gentle movement, yoga, and breathwork can access it.
        Healing is not linear — setbacks are part of recovery, not proof that healing isn't working.
        Seek a trauma-specialized therapist (EMDR-certified or trauma-focused CBT trained) for best outcomes.""",
        "metadata": {"category": "condition", "type": "trauma"},
    },
    {
        "id": "grief-loss-001",
        "content": """Grief and loss: navigating bereavement and major life transitions:
        Grief is not a disorder — it is love with nowhere to go. There is no right way to grieve.
        Kübler-Ross's stages (denial, anger, bargaining, depression, acceptance) are not a linear checklist — they are possible experiences.
        Complicated grief (prolonged grief disorder): when grief severely impairs functioning beyond 12 months, therapy can help.
        Types of grief: bereavement, disenfranchised grief (losses not socially recognized), ambiguous loss, anticipatory grief.
        What actually helps: letting yourself feel emotions without rushing them, maintaining routine, accepting support.
        What doesn't help: 'staying strong', suppressing feelings, timelines imposed by others ('you should be over it by now').
        Continuing bonds theory: maintaining a relationship with the deceased through memory and ritual is healthy, not 'stuck'.
        Anniversary reactions are normal — grief tends to resurface at significant dates.
        Grief support: GriefShare groups, Compassionate Friends (child loss), AFSP (suicide loss survivors).""",
        "metadata": {"category": "condition", "type": "grief"},
    },
    {
        "id": "emotional-regulation-001",
        "content": """Emotional regulation skills (DBT-informed):
        Dialectical Behavior Therapy (DBT) offers some of the most practical emotion regulation tools available.
        TIPP for intense emotions: Temperature (cold water on face/wrists), Intense exercise, Paced breathing, Progressive relaxation.
        Opposite action: when an emotion urges you to do something harmful (isolate when lonely, avoid when anxious), do the opposite.
        Check the facts: ask 'Does my emotional response fit the situation?' Emotions can misfire based on past experiences.
        Build positive emotions: deliberately schedule activities that bring mastery and pleasure — don't wait to feel motivated.
        Reduce emotional vulnerability (PLEASE): treat PhysicaL illness, balance Eating, avoid mood-Altering substances, balance Sleep, get Exercise.
        Ride the wave: emotions are time-limited — the average emotional peak lasts 90 seconds before the wave begins to subside.
        Mindfulness of emotion: observe the emotion without judging it or acting on it ('I notice I am feeling fear').
        Emotion naming (affect labeling): simply naming an emotion in words reduces activity in the amygdala.""",
        "metadata": {"category": "techniques", "type": "emotional-regulation"},
    },
]
