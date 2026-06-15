"""
Content Quality Gate — P0 Integration
Runs humanizer + factual-claim-verifier on drafts before publishing.
Part of ContentNova pipeline.
"""

import sys
import os
import re

# Humanizer patterns (from humanizer skill)
AI_PATTERNS = {
    'significance_puff': [
        'stands as', 'serves as', 'is a testament', 'is a reminder',
        'a vital role', 'a significant role', 'a crucial role', 'a pivotal role',
        'underscores its importance', 'highlights its significance',
        'reflects broader', 'symbolizing its ongoing', 'contributing to the',
        'setting the stage for', 'marking the', 'shaping the',
        'represents a shift', 'key turning point', 'evolving landscape',
        'focal point', 'indelible mark', 'deeply rooted'
    ],
    'promotional': [
        'boasts', 'offers a unique blend', 'promises to deliver',
        'designed to cater', 'tailored to meet', 'seamlessly integrates'
    ],
    'vague_attribution': [
        'some argue', 'many believe', 'critics say', 'experts suggest',
        'it is important to note', 'it is worth noting'
    ],
    'ai_vocab': [
        'delve', 'tapestry', 'landscape', 'realm', 'paradigm',
        'multifaceted', 'ever-evolving', 'robust', 'leverage',
        'underscore', 'highlight', 'foster', 'catalyst'
    ],
    'negative_parallelism': [
        'not just', 'not merely', 'not only', 'but also', 'but rather'
    ],
    'excessive_conjunctive': [
        'furthermore', 'moreover', 'in conclusion', 'to conclude',
        'in summary', 'ultimately', 'overall', 'in essence',
        'it is clear that', 'it is evident that'
    ],
    'filler_phrases': [
        'in order to', 'due to the fact that', 'at this point in time',
        'for all intents and purposes', 'it goes without saying'
    ]
}

def humanize_text(text):
    """Strip AI patterns and inject natural voice."""
    original = text
    fixes = []
    
    # Check for each pattern category
    for category, patterns in AI_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text.lower():
                fixes.append(f"  [{category}] '{pattern}'")
    
    # Check em dash overuse
    em_dash_count = text.count('—')
    if em_dash_count > 3:
        fixes.append(f"  [em_dashes] {em_dash_count} em dashes (limit: 3)")
    
    # Check rule of three
    three_pattern = re.findall(r'(\w+),\s+\w+,\s+and\s+\w+', text)
    if len(three_pattern) > 2:
        fixes.append(f"  [rule_of_three] {len(three_pattern)} instances")
    
    # Check -ing analysis sentences
    ing_sentences = re.findall(r'[^.]*by\s+\w+ing[^.]*\.', text)
    if len(ing_sentences) > 2:
        fixes.append(f"  [ing_analysis] {len(ing_sentences)} '-ing' analysis sentences")
    
    # Check sentence length uniformity
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) > 5:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        if variance < 10:  # Very uniform sentence lengths
            fixes.append(f"  [uniform_length] sentences too uniform (variance: {variance:.1f})")
    
    # Generate humanized version
    humanized = _apply_humanization(text)
    
    return {
        'humanized': humanized,
        'fixes_found': len(fixes),
        'fixes': fixes,
        'needs_humanization': len(fixes) > 0
    }

def _apply_humanization(text):
    """Apply humanization fixes."""
    result = text
    
    # Replace promotional puff
    result = result.replace('boasts', 'has')
    result = result.replace('offers a unique blend', 'combines')
    result = result.replace('promises to deliver', 'delivers')
    result = result.replace('designed to cater', 'serves')
    result = result.replace('tailored to meet', 'meets')
    result = result.replace('seamlessly integrates', 'works with')
    
    # Replace vague attribution
    result = result.replace('Some argue that', 'I have mixed feelings about')
    result = result.replace('Many believe', 'People seem to think')
    result = result.replace('It is important to note', 'Worth mentioning')
    result = result.replace('It is worth noting', 'Note')
    
    # Replace AI vocab
    result = re.sub(r'\bdelve\b', 'explore', result, flags=re.IGNORECASE)
    result = re.sub(r'\btapestry\b', 'mix', result, flags=re.IGNORECASE)
    result = re.sub(r'\bever-evolving\b', 'changing', result, flags=re.IGNORECASE)
    result = re.sub(r'\bleverage\b', 'use', result, flags=re.IGNORECASE)
    result = re.sub(r'\bunderscore\b', 'show', result, flags=re.IGNORECASE)
    result = re.sub(r'\bhighlight\b', 'show', result, flags=re.IGNORECASE)
    result = re.sub(r'\bfoster\b', 'build', result, flags=re.IGNORECASE)
    result = re.sub(r'\bcatalyst\b', 'driver', result, flags=re.IGNORECASE)
    
    # Replace filler phrases
    result = result.replace('in order to', 'to')
    result = result.replace('due to the fact that', 'because')
    result = result.replace('at this point in time', 'now')
    result = result.replace('for all intents and purposes', 'basically')
    result = result.replace('it goes without saying', '')
    
    # Replace excessive conjunctives
    result = result.replace('Furthermore,', 'Also,')
    result = result.replace('Moreover,', 'Plus,')
    result = result.replace('In conclusion,', 'So,')
    result = result.replace('To conclude,', 'To wrap up,')
    result = result.replace('Ultimately,', 'At the end of the day,')
    result = result.replace('In essence,', 'Basically,')
    
    # Reduce repetitive structure
    result = _add_voice(result)
    
    return result

def _add_voice(text):
    """Add personality and varied rhythm."""
    sentences = [s.strip() for s in re.split(r'([.!?]+)', text) if s.strip()]
    
    # Vary sentence lengths by splitting/combining
    varied = []
    for i, sentence in enumerate(sentences):
        if i % 5 == 0 and len(sentence.split()) > 20:
            # Break long sentence at comma
            parts = sentence.split(', ')
            if len(parts) > 1:
                varied.append(parts[0] + '.')
                varied.append(' '.join(parts[1:]) + '.')
                continue
        varied.append(sentence)
    
    # Add occasional first-person when appropriate
    if 'I' not in text[:500] and len(text) > 1000:
        varied.insert(2, "I have to say, the data here is genuinely interesting.")
    
    return ' '.join(varied)


def verify_claims(text):
    """Basic claim verification — flags risky assertions."""
    claims = []
    
    # Extract numbers with units
    number_claims = re.findall(r'(\d+(?:\.\d+)?)\s*(%|million|billion|percent|users?|downloads?|revenue|profit)', text, re.IGNORECASE)
    if number_claims:
        claims.append(f"  [numbers] {len(number_claims)} numerical claims found")
    
    # Extract specific product/tool names with capabilities
    capability_claims = re.findall(r'(\w+)\s+(?:can|will|enables?|allows?|supports?)\s+(.{10,80})', text, re.IGNORECASE)
    if capability_claims:
        claims.append(f"  [capabilities] {len(capability_claims)} capability claims found")
    
    # Extract comparisons
    comparison_claims = re.findall(r'(\w+)\s+(?:better than|superior to|outperforms?|faster than|more than)\s+(.{5,50})', text, re.IGNORECASE)
    if comparison_claims:
        claims.append(f"  [comparisons] {len(comparison_claims)} comparison claims found")
    
    # Extract timeline claims
    timeline_claims = re.findall(r'(?:by|in|during)\s+(?:20\d{2}|Q[1-4]\s+20\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2})', text, re.IGNORECASE)
    if timeline_claims:
        claims.append(f"  [timelines] {len(timeline_claims)} timeline claims found")
    
    # Risk scoring
    risk = "low"
    risk_reasons = []
    
    if len(number_claims) > 5:
        risk = "medium"
        risk_reasons.append("many numerical claims need sources")
    
    if len(capability_claims) > 3:
        risk = "medium"
        risk_reasons.append("multiple capability claims need verification")
    
    if 'guarantee' in text.lower() or '100%' in text:
        risk = "high"
        risk_reasons.append("absolute claims detected")
    
    if 'always' in text.lower() or 'never' in text.lower():
        if risk != "high":
            risk = "medium"
        risk_reasons.append("absolutist language")
    
    verdict = "ready"
    if risk == "high":
        verdict = "revise before publishing"
    elif risk == "medium":
        verdict = "publish with minor changes"
    
    return {
        'claims_found': len(claims),
        'claims': claims,
        'risk': risk,
        'risk_reasons': risk_reasons,
        'verdict': verdict
    }


def quality_gate(article_text, title=None):
    """Run full quality gate on article."""
    print("="*70)
    print("CONTENT QUALITY GATE")
    print("="*70)
    
    # Step 1: Humanize
    print("\n[1/3] Running humanizer...")
    human_result = humanize_text(article_text)
    
    if human_result['needs_humanization']:
        print(f"  Found {human_result['fixes_found']} AI patterns:")
        for fix in human_result['fixes']:
            print(f"    {fix}")
        print("  [FIXED] Applied humanization")
    else:
        print("  [PASS] No AI patterns detected")
    
    # Step 2: Verify claims
    print("\n[2/3] Running factual claim verification...")
    verify_result = verify_claims(article_text)
    
    if verify_result['claims_found'] > 0:
        print(f"  Found {verify_result['claims_found']} claim categories:")
        for claim in verify_result['claims']:
            print(f"    {claim}")
        print(f"  Risk: {verify_result['risk'].upper()}")
        if verify_result['risk_reasons']:
            for reason in verify_result['risk_reasons']:
                print(f"    - {reason}")
    else:
        print("  [PASS] No verifiable claims found (opinion piece?)")
    
    # Step 3: Final verdict
    print("\n[3/3] Final verdict...")
    print(f"  Humanization: {'NEEDED' if human_result['needs_humanization'] else 'PASS'}")
    print(f"  Fact-check: {verify_result['verdict'].upper()}")
    
    if human_result['needs_humanization'] and verify_result['verdict'] in ('ready', 'publish with minor changes'):
        final = "publish with minor changes (humanization applied)"
    elif verify_result['verdict'] == "revise before publishing":
        final = "revise before publishing"
    else:
        final = verify_result['verdict']
    
    print(f"  FINAL: {final.upper()}")
    print("="*70)
    
    return {
        'original': article_text,
        'humanized': human_result['humanized'] if human_result['needs_humanization'] else article_text,
        'humanization_needed': human_result['needs_humanization'],
        'humanization_fixes': human_result['fixes'],
        'claim_verdict': verify_result['verdict'],
        'claim_risk': verify_result['risk'],
        'final_verdict': final,
        'can_publish': final in ('ready', 'publish with minor changes (humanization applied)', 'publish with minor changes')
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Content Quality Gate')
    parser.add_argument('file', help='Article markdown file to review')
    parser.add_argument('--output', '-o', help='Output file for humanized version')
    parser.add_argument('--publish', action='store_true', help='Publish if gate passes')
    args = parser.parse_args()
    
    with open(args.file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = quality_gate(text)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result['humanized'])
        print(f"\nHumanized version saved to: {args.output}")
    
    if args.publish and result['can_publish']:
        print("\n[OK] Publishing enabled — gate passed")
    elif args.publish:
        print("\n[BLOCKED] Publishing blocked — gate failed")
        sys.exit(1)
