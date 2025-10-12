"""
🧪 TEST SCRIPT - Verify Option Generation Fix
Run this to test if answers are generated properly
"""

import sys
sys.path.insert(0, 'f:/ai_aptitude_exam/project')

from fast_ai_generator import FastAIGenerator

def test_option_generation():
    """Test that options are generated correctly"""
    print("\n" + "="*80)
    print("🧪 TESTING OPTION GENERATION")
    print("="*80 + "\n")
    
    generator = FastAIGenerator()
    
    # Test context
    test_context = """
    Binary Search is an efficient algorithm for finding an item in a sorted array.
    It works by repeatedly dividing the search interval in half. If the target value
    is less than the middle element, search the left half; otherwise search the right.
    Time complexity is O(log n).
    """
    
    print("📝 Test Context:")
    print(test_context.strip())
    print("\n" + "-"*80 + "\n")
    
    # Generate a question
    print("⚡ Generating question...")
    q_data = generator.generate_fast(test_context, "Algorithms")
    
    if not q_data:
        print("❌ FAILED: No question generated")
        return False
    
    # Check all fields
    print("✅ Question generated successfully!\n")
    print(f"Question: {q_data['question']}")
    print(f"\nOptions:")
    print(f"  A) {q_data['option_a']}")
    print(f"  B) {q_data['option_b']}")
    print(f"  C) {q_data['option_c']}")
    print(f"  D) {q_data['option_d']}")
    print(f"\nCorrect Answer: {q_data['correct_option'].upper()}")
    print(f"Topic: {q_data['topic']}")
    print(f"Difficulty: {q_data['difficulty']}")
    print(f"Quality Score: {q_data.get('quality_score', 'N/A')}")
    
    # Verify all options exist and are not empty
    checks = []
    checks.append(("option_a exists", q_data['option_a'] and len(q_data['option_a']) > 0))
    checks.append(("option_b exists", q_data['option_b'] and len(q_data['option_b']) > 0))
    checks.append(("option_c exists", q_data['option_c'] and len(q_data['option_c']) > 0))
    checks.append(("option_d exists", q_data['option_d'] and len(q_data['option_d']) > 0))
    checks.append(("correct_option valid", q_data['correct_option'] in ['a', 'b', 'c', 'd']))
    checks.append(("question exists", q_data['question'] and len(q_data['question']) > 20))
    
    print("\n" + "-"*80)
    print("🔍 VALIDATION CHECKS:")
    print("-"*80)
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Option generation is working correctly.")
    else:
        print("⚠️ SOME CHECKS FAILED. Review the output above.")
    print("="*80 + "\n")
    
    return all_passed


def test_multiple_questions():
    """Test generating multiple questions"""
    print("\n" + "="*80)
    print("🧪 TESTING MULTIPLE QUESTION GENERATION")
    print("="*80 + "\n")
    
    generator = FastAIGenerator()
    
    test_topics = [
        ("Data Structures", "Arrays store elements in contiguous memory locations with O(1) access time."),
        ("Algorithms", "Quick Sort uses divide-and-conquer strategy with O(n log n) average time complexity."),
        ("Databases", "SQL queries retrieve data using SELECT statements with WHERE clauses for filtering.")
    ]
    
    generated_count = 0
    failed_count = 0
    
    for topic, context in test_topics:
        print(f"📝 Generating for topic: {topic}")
        q_data = generator.generate_fast(context, topic)
        
        if q_data and q_data['option_a'] and q_data['option_b']:
            print(f"   ✅ Generated: {q_data['question'][:60]}...")
            print(f"   ✅ Options: {q_data['option_a'][:30]}... | {q_data['option_b'][:30]}...")
            generated_count += 1
        else:
            print(f"   ❌ Failed to generate")
            failed_count += 1
        print()
    
    print("-"*80)
    print(f"📊 Results: {generated_count}/{len(test_topics)} successful")
    
    if generated_count >= 2:
        print("🎉 Multiple generation working!")
        return True
    else:
        print("⚠️ Multiple generation needs attention")
        return False


if __name__ == '__main__':
    print("\n🚀 Starting Option Generation Tests...\n")
    
    try:
        test1_passed = test_option_generation()
        test2_passed = test_multiple_questions()
        
        print("\n" + "="*80)
        print("📋 FINAL RESULTS")
        print("="*80)
        print(f"Single Question Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"Multiple Question Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED! The fix is working correctly.")
            print("✅ You can now restart the Flask app and test in the UI.")
        else:
            print("\n⚠️ Some tests failed. Check the output above for details.")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
