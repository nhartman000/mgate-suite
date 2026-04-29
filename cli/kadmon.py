#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.environment import KadmonEnvironment

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <command> [args]")
        print("\nCommands:")
        print("  start                      Start Kadmon environment")
        print("  pair <model1> <model2>     Run PAIR mode dual LLM negotiation")
        print("  run <mg8_path>             Execute MGATE within Kadmon")
        print("  status                     Show environment status")
        sys.exit(1)
        
    command = sys.argv[1]
    
    env = KadmonEnvironment()
    env.start()
    
    print(f"Kadmon Environment started")
    print(f"  Environment ID: {env.environment_id}")
    print(f"  Center Point: {env.center_point}")
    print(f"  Run Trace: {env.run_trace_id}")
    print()
    
    if command == "start":
        print("Environment initialized successfully")
        
    elif command == "pair":
        if len(sys.argv) != 4:
            print("Usage: kadmon.py pair <model1> <model2>")
            sys.exit(1)
            
        model1 = sys.argv[2]
        model2 = sys.argv[3]
        
        print(f"Creating PAIR configuration: {model1} + {model2}")
        pair = env.create_pair(model1, model2, mode="PAIR")
        
        print(f"Running negotiation...")
        result = env.run_negotiation(pair)
        
        print(f"\nNegotiation complete:")
        print(f"  Consensus reached: {result['consensus']}")
        print(f"  Rounds: {result['rounds']}")
        
        if result['consensus']:
            print(f"  Agreed position: {result['agreed_position']}")
            print(f"  Stability: {result['stability']['mathematical']}")
        
    elif command == "run":
        if len(sys.argv) != 3:
            print("Usage: kadmon.py run <mg8_path>")
            sys.exit(1)
            
        mg8_path = sys.argv[2]
        print(f"Executing MGATE: {mg8_path}")
        
        result = env.execute_mgate(mg8_path)
        print(f"Execution complete. {len(result['events'])} events logged.")
        
    elif command == "status":
        print(f"Second order systems: {len(env.contained_systems['second_order'])}")
        print(f"Third order systems: {len(env.contained_systems['third_order'])}")
        print(f"Fourth order systems: {len(env.contained_systems['fourth_order'])}")
        
    env.shutdown()

if __name__ == "__main__":
    main()
