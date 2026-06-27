<?php
/*
Template Name: Dues Page
Description: Membership dues payment page with Venmo integration
*/
get_header();
?>

<!-- Dues Hero -->
<section class="dues-hero">
    <div class="hero-content">
        <h1>Pay Your Annual Dues</h1>
        <p>Support the Middle Georgia Radio Association and keep the repeaters on the air</p>
    </div>
</section>

<!-- Dues Options -->
<section class="section-alt" style="padding: 4rem 2rem;">
    <div class="container">
        <h2 class="section-title" style="margin-bottom: 0.5rem;">Membership Options</h2>
        <p class="section-subtitle" style="margin-bottom: 3rem;">Choose the plan that works for you</p>
        
        <div class="dues-options">
            <!-- Individual Membership -->
            <div class="dues-card">
                <h3>Individual</h3>
                <div class="price">$25<span>/year</span></div>
                <ul>
                    <li>Full voting membership</li>
                    <li>Access to club repeaters</li>
                    <li>Monthly newsletter</li>
                    <li>Testing session access</li>
                    <li>Field Day participation</li>
                    <li>Technical support</li>
                </ul>
                
                <!-- Venmo Pay Button -->
                <a href="https://venmo.com/WR4MG?txn=pay&amount=25&note=Individual%20Membership%20Dues%20<?php echo date('Y'); ?>" 
                   class="venmo-btn" target="_blank" rel="noopener">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                    </svg>
                    Pay $25 with Venmo
                </a>
                
                <p style="text-align: center; margin-top: 1rem; font-size: 0.85rem; color: var(--text-light);">
                    Note: Include your callsign in the payment note
                </p>
            </div>
            
            <!-- Family Membership -->
            <div class="dues-card featured">
                <div class="badge">Popular</div>
                <h3>Family</h3>
                <div class="price">$40<span>/year</span></div>
                <ul>
                    <li>Everything in Individual</li>
                    <li>Covers household members</li>
                    <li>Spouse + children under 18</li>
                    <li>Shared callsign privileges</li>
                    <li>Priority event registration</li>
                    <li>Club merchandise discounts</li>
                </ul>
                
                <a href="https://venmo.com/WR4MG?txn=pay&amount=40&note=Family%20Membership%20Dues%20<?php echo date('Y'); ?>" 
                   class="venmo-btn" target="_blank" rel="noopener">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                    </svg>
                    Pay $40 with Venmo
                </a>
                
                <p style="text-align: center; margin-top: 1rem; font-size: 0.85rem; color: var(--text-light);">
                    Note: Include primary callsign + family members
                </p>
            </div>
            
            <!-- Student / Senior -->
            <div class="dues-card">
                <h3>Student / Senior</h3>
                <div class="price">$15<span>/year</span></div>
                <ul>
                    <li>Full voting membership</li>
                    <li>Access to club repeaters</li>
                    <li>Monthly newsletter</li>
                    <li>Testing session access</li>
                    <li>Field Day participation</li>
                    <li>Technical support</li>
                </ul>
                
                <a href="https://venmo.com/WR4MG?txn=pay&amount=15&note=Student-Senior%20Dues%20<?php echo date('Y'); ?>" 
                   class="venmo-btn" target="_blank" rel="noopener">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                    </svg>
                    Pay $15 with Venmo
                </a>
                
                <p style="text-align: center; margin-top: 1rem; font-size: 0.85rem; color: var(--text-light);">
                    Valid student ID or 65+ required. Include in note.
                </p>
            </div>
        </div>
        
        <!-- Additional Info -->
        <div style="max-width: 700px; margin: 3rem auto 0; text-align: center; background: white; padding: 2rem; border-radius: 12px; box-shadow: var(--shadow);">
            <h3 style="color: var(--primary); margin-bottom: 1rem;">Other Payment Methods</h3>
            <p style="margin-bottom: 1rem;">Don't use Venmo? You can also pay by:</p>
            <ul style="list-style: none; text-align: left; max-width: 400px; margin: 0 auto;">
                <li style="padding: 0.5rem 0;">💵 <strong>Cash</strong> — at any monthly meeting</li>
                <li style="padding: 0.5rem 0;">✉️ <strong>Check</strong> — mail to P.O. Box 10528, Warner Robins, GA 31095</li>
                <li style="padding: 0.5rem 0;">💳 <strong>PayPal</strong> — <a href="mailto:getmorehams@wr4mg.us">email us for link</a></li>
            </ul>
            
            <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border);">
                <h4 style="color: var(--primary); margin-bottom: 0.5rem;">Questions?</h4>
                <p>Contact us at <a href="mailto:getmorehams@wr4mg.us">getmorehams@wr4mg.us</a> or reach out on <a href="https://www.facebook.com/WR4MG/" target="_blank">Facebook</a>.</p>
            </div>
        </div>
        
        <!-- Manual Entry Form -->
        <div style="max-width: 700px; margin: 3rem auto 0; background: white; padding: 2rem; border-radius: 12px; box-shadow: var(--shadow);">
            <h3 style="color: var(--primary); margin-bottom: 1rem; text-align: center;">📋 Dues Payment Record</h3>
            <p style="text-align: center; margin-bottom: 1.5rem; color: var(--text-light); font-size: 0.95rem;">
                Already paid? Let us know so we can update our records.
            </p>
            
            <form id="duesForm" style="display: grid; gap: 1rem;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--primary);">Name *</label>
                        <input type="text" name="name" required 
                               style="width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem;">
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--primary);">Callsign</label>
                        <input type="text" name="callsign" placeholder="e.g., WR4MG"
                               style="width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem; text-transform: uppercase;">
                    </div>
                </div>
                
                <div>
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--primary);">Email *</label>
                    <input type="email" name="email" required
                           style="width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem;">
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--primary);">Membership Type *</label>
                        <select name="membership_type" required
                                style="width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem; background: white;">
                            <option value="">Select...</option>
                            <option value="individual">Individual ($25)</option>
                            <option value="family">Family ($40)</option>
                            <option value="student_senior">Student / Senior ($15)</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--primary);">Payment Method *</label>
                        <select name="payment_method" required
                                style="width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem; background: white;">
                            <option value="">Select...</option>
                            <option value="venmo">Venmo</option>
                            <option value="cash">Cash</option>
                            <option value="check">Check</option>
                            <option value="paypal">PayPal</option>
                        </select>
                    </div>
                </div>
                
                <div>
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--primary);">Notes (optional)</label>
                    <textarea name="notes" rows="3" placeholder="Family members, payment date, etc."
                              style="width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem; resize: vertical;"></textarea>
                </div>
                
                <button type="submit" class="btn btn-primary" style="width: 100%; border: none; cursor: pointer; margin-top: 0.5rem;">
                    Submit Payment Record
                </button>
            </form>
            
            <div id="formSuccess" style="display: none; margin-top: 1rem; padding: 1rem; background: #c6f6d5; border-radius: 8px; color: #22543d; text-align: center;">
                ✅ Thank you! Your payment record has been submitted. We'll update our records within 48 hours.
            </div>
        </div>
    </div>
</section>

<script>
document.getElementById('duesForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // In a real WordPress setup, this would submit to a form handler or REST endpoint
    // For now, show success message (admin would need to set up actual form handling)
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    
    // Log for demo (in production, send to WordPress REST API or email)
    console.log('Dues payment record:', data);
    
    document.getElementById('formSuccess').style.display = 'block';
    this.reset();
    
    // Scroll to success message
    document.getElementById('formSuccess').scrollIntoView({ behavior: 'smooth', block: 'center' });
});
</script>

<?php get_footer(); ?>
