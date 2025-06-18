def approval(state: dict) -> dict:
    print("Inside Human Approval")

    optimized = state.get("optimized", True)

    if optimized:
        print("Final Itinerary (Optimized):")
        itinerary = state.get("final_itenary", "No itinerary available.")
        print(itinerary)
    else:
        print("⚠️ Optimization failed, showing simple POI list:")
        pois = state.get("points_of_interest", [])
        if pois:
            for i, place in enumerate(pois, 1):
                print(f"{i}. {place}")
        else:
            print("No POIs available.")

    feedback = input("Enter your feedback (or type 'approve' if happy): ").strip()

    if not feedback:
        feedback = "approve"

    message_history = state.get("message_history", [])
    message_history.append({"role": "user", "content": feedback})

    return {
        **state,
        "human_feedback": feedback,
        "human_decision": "approve" if feedback.lower() == "approve" else "replan",
        "message_history": message_history
    }
