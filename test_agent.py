#!/usr/bin/env python3
"""
Simple test script for the Vertex AI emotion detection agent.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_emotion_agent():
    """Test the emotion detection agent."""
    print("🎭 Testing Vertex AI Emotion Detection Agent")
    print("=" * 50)

    # Check environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    if not project_id:
        print("❌ Please set GOOGLE_CLOUD_PROJECT in your .env file")
        print("   Also run: gcloud auth application-default login")
        return

    print(f"✅ Project ID: {project_id}")

    try:
        from google.adk.runners import InMemoryRunner
        from ai_companion.agent import root_agent

        # Create a runner
        runner = InMemoryRunner(
            app_name="Emotion Detection Test",
            agent=root_agent,
        )

        # Create a session
        session = await runner.session_service.create_session(
            app_name="Emotion Detection Test",
            user_id="test_user",
        )

        # Test conversation scenarios to demonstrate context awareness
        conversation_scenarios = [
            {
                "name": "Single Message Test",
                "messages": ["I'm absolutely thrilled about my promotion!"],
            },
            {
                "name": "Ambiguous Message with Context",
                "messages": [
                    "I've been working on this project for months.",
                    "The deadline is tomorrow and I'm not sure if I'll finish.",
                    "Fine.",
                ],
            },
            {
                "name": "Emotional Escalation",
                "messages": [
                    "The meeting went okay I guess.",
                    "Actually, they didn't seem to like my ideas.",
                    "I can't believe they dismissed everything I said!",
                ],
            },
            {
                "name": "Emotional Transition",
                "messages": [
                    "I'm so excited about the concert tonight!",
                    "Oh no, it just got cancelled.",
                    "Well, I guess I'll just stay home then.",
                ],
            },
            {
                "name": "Context-Dependent Sarcasm",
                "messages": [
                    "I studied all night for this exam.",
                    "I felt really confident going in.",
                    "Yeah, that went great.",
                ],
            },
        ]

        print("\nTesting emotion detection with conversation context:")
        print("-" * 60)

        for scenario_idx, scenario in enumerate(conversation_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"Scenario {scenario_idx}: {scenario['name']}")
            print(f"{'='*60}")

            # Create a new session for each scenario to test conversation context
            scenario_session = await runner.session_service.create_session(
                app_name="Emotion Detection Test",
                user_id=f"test_user_scenario_{scenario_idx}",
            )

            for msg_idx, message in enumerate(scenario["messages"], 1):
                print(f'\nMessage {msg_idx}: "{message}"')
                print("-" * 40)

                try:
                    # Run the agent with conversation history
                    result = await runner.run(
                        session=scenario_session, user_input=message
                    )

                    # Parse the structured response
                    if hasattr(result, "text") and result.text:
                        import json

                        try:
                            response_data = json.loads(result.text)
                            print(
                                f"   🎯 Primary: {response_data.get('primary_emotion', 'unknown')}"
                            )
                            print(
                                f"   📊 Confidence: {response_data.get('confidence', 'unknown')}"
                            )
                            print(
                                f"   🔥 Intensity: {response_data.get('intensity', 'unknown')}/10"
                            )

                            if response_data.get("secondary_emotions"):
                                print(
                                    f"   🔄 Secondary: {response_data.get('secondary_emotions')}"
                                )

                            print(
                                f"   📝 Analysis: {response_data.get('analysis', 'No analysis')}"
                            )

                            # Show conversation context fields
                            if response_data.get("context_influence"):
                                print(
                                    f"   🔗 Context Influence: {response_data.get('context_influence')}"
                                )

                            if response_data.get("emotional_trajectory"):
                                print(
                                    f"   📈 Emotional Trajectory: {response_data.get('emotional_trajectory')}"
                                )

                            if "conversation_sentiment" in response_data:
                                sentiment = response_data.get(
                                    "conversation_sentiment", 0
                                )
                                print(f"   💭 Conversation Sentiment: {sentiment:.2f}")

                            if response_data.get("emotional_indicators"):
                                print(
                                    f"   🔍 Indicators: {response_data.get('emotional_indicators')}"
                                )

                        except json.JSONDecodeError:
                            print(f"   📄 Raw Response: {result.text}")
                    else:
                        print(f"   📄 Response: {result}")

                except Exception as e:
                    print(f"   ❌ Error: {e}")

                # Add a small delay between messages in the same conversation
                if msg_idx < len(scenario["messages"]):
                    import asyncio

                    await asyncio.sleep(0.5)

        print("\n" + "=" * 60)
        print("✅ Conversation context testing completed!")
        print("\n💡 Key insights:")
        print("   - Single messages vs. conversation context")
        print("   - How ambiguous messages are interpreted with history")
        print("   - Emotional escalation and de-escalation patterns")
        print("   - Context-dependent emotion detection (sarcasm, implications)")
        print("   - Emotional trajectory tracking across conversations")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Main function."""
    asyncio.run(test_emotion_agent())


if __name__ == "__main__":
    main()
