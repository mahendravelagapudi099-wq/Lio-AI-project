from Backend.StateManager import StateManager

def test_readiness():
    state_mgr = StateManager()
    state = state_mgr.GetState()
    
    print("Initial State:", state)
    
    if "readiness" in state:
        print("Readiness flags found:", state["readiness"])
        
        state_mgr.SetReadiness("cloud", True)
        updated_state = state_mgr.GetState()
        print("Updated Cloud Readiness:", updated_state["readiness"]["cloud"])
        
        if updated_state["readiness"]["cloud"] == True:
            print("TEST PASSED")
        else:
            print("TEST FAILED: cloud readiness not updated")
    else:
        print("TEST FAILED: readiness key not found in state")

if __name__ == "__main__":
    test_readiness()
