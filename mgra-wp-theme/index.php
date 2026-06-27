<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php wp_title('|', true, 'right'); ?><?php bloginfo('name'); ?></title>
    <link rel="stylesheet" href="<?php echo get_stylesheet_uri(); ?>">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?> id="page-top">

    <!-- Navigation -->
    <nav class="main-nav">
        <a href="#page-top" class="nav-brand">MGRA <span>WR4MG</span></a>
        <button class="mobile-menu-btn" onclick="toggleMenu()">☰</button>
        <ul class="nav-links" id="navMenu">
            <li><a href="#home">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#repeaters">Repeaters</a></li>
            <li><a href="#events">Calendar</a></li>
            <li><a href="#photos">Photos</a></li>
            <li><a href="#links">Links</a></li>
            <li><a href="<?php echo site_url('/dues'); ?>">Pay Dues</a></li>
            <li><a href="#footer">Contact</a></li>
        </ul>
    </nav>

    <!-- Hero Section -->
    <header class="hero" id="home">
        <div class="hero-content">
            <h1>Middle Georgia Radio Association</h1>
            <span class="call-sign">WR4MG</span>
            <div class="hero-buttons">
                <a href="https://www.facebook.com/WR4MG/" class="btn btn-primary" target="_blank">Visit Us On Facebook</a>
                <a href="#footer" class="btn btn-outline">Contact Us</a>
                <a href="#links" class="btn btn-accent">Join Us</a>
            </div>
        </div>
    </header>

    <!-- About Section -->
    <section id="about">
        <div class="container">
            <h2 class="section-title">About the MGRA</h2>
            <div class="about-content">
                <div class="about-text">
                    <p><strong>NOTE:</strong> MGRA meets the third Thursday of every month at 7pm at the Warner Robins Church of Christ. If this is your first meeting you can reach out to us on Facebook or Email for more information.</p>
                    
                    <p>The Middle Georgia Radio Association was formed as a different kind of radio club, one focused on technical and operational radio fundamentals. We offer monthly testing sessions at <strong>zero cost</strong> every month if you want to earn your amateur radio operator license!</p>
                    
                    <p>Our main mission is to provide an educational environment to the public along with ham radio operators throughout the area to learn, experiment, and enjoy the art of amateur radio. We offer technical seminars, public education/exposure, operating events, field day, special events, emergency communication prep, and help with station setups.</p>
                    
                    <p>We are active on the air, on social media, and on email to keep everyone in the know. During the week you will find the MGRA repeaters the most active with technical discussions in Middle Georgia and provide an easy link to reaching out to us.</p>
                    
                    <p>We hope that you can find a place with us — to nurture the hobby of radio communication so that it may be enjoyed and thrive for many more generations to enjoy.</p>
                </div>
                <div class="about-sidebar">
                    <h3>New to Ham Radio?</h3>
                    <p>✓ Monthly testing sessions — <strong>FREE</strong></p>
                    <p>✓ Technical seminars & public education</p>
                    <p>✓ Operating events & Field Day</p>
                    <p>✓ Emergency communication prep</p>
                    <p>✓ Station setup assistance</p>
                    <p style="margin-top: 1.5rem;">
                        <a href="<?php echo site_url('/dues'); ?>" class="btn btn-primary">Pay Annual Dues →</a>
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Repeaters Section -->
    <section id="repeaters" class="section-alt">
        <div class="container">
            <h2 class="section-title">Middle Georgia Repeaters</h2>
            <p class="section-subtitle">Active repeaters in the Middle Georgia area</p>
            
            <table class="repeater-table">
                <thead>
                    <tr>
                        <th>Frequency</th>
                        <th>PL Tone</th>
                        <th>Location</th>
                        <th>Callsign & Info</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="freq">147.300+</td>
                        <td>107.2</td>
                        <td>Centerville, GA</td>
                        <td>WR4MG — Echolink node WR4MG-R</td>
                    </tr>
                    <tr>
                        <td class="freq">146.955-</td>
                        <td>107.2</td>
                        <td>Perry, GA</td>
                        <td>WR4MG — Echolink node WR4MG-L</td>
                    </tr>
                    <tr>
                        <td class="freq">442.900+</td>
                        <td>107.2</td>
                        <td>Warner Robins, GA</td>
                        <td>WR4MG</td>
                    </tr>
                    <tr>
                        <td class="freq">440.575+</td>
                        <td>82.5*</td>
                        <td>Houston County EOC</td>
                        <td>WY4EMA — DMR, DSTAR, and FM</td>
                    </tr>
                    <tr>
                        <td class="freq">444.950+</td>
                        <td>107.2</td>
                        <td>Butler, GA</td>
                        <td>WR4MG</td>
                    </tr>
                    <tr>
                        <td class="freq">147.195+</td>
                        <td>107.2</td>
                        <td>Butler, GA</td>
                        <td>WR4MG</td>
                    </tr>
                    <tr>
                        <td class="freq">147.180+</td>
                        <td>No tone</td>
                        <td>Warner Robins, GA</td>
                        <td>WB4BDP</td>
                    </tr>
                    <tr>
                        <td class="freq">146.850-</td>
                        <td>82.5</td>
                        <td>Warner Robins, GA</td>
                        <td>WA4ORT</td>
                    </tr>
                    <tr>
                        <td class="freq">146.670-</td>
                        <td>82.5</td>
                        <td>Warner Robins, GA</td>
                        <td>WM4B — Intertie Link active for ARES Nets</td>
                    </tr>
                    <tr>
                        <td class="freq">443.150+</td>
                        <td>82.5</td>
                        <td>Warner Robins, GA</td>
                        <td>WM4B</td>
                    </tr>
                    <tr>
                        <td class="freq">145.290-</td>
                        <td>82.5</td>
                        <td>Byron, GA</td>
                        <td>WX4PCH</td>
                    </tr>
                </tbody>
            </table>
            <p class="pl-note" style="text-align: center; margin-top: 1rem; color: var(--text-light);">* PL tone 82.5 for FM mode on WY4EMA</p>
            <p style="text-align: center; margin-top: 1rem;">
                <a href="http://www.kk4ib.org/RPTR&FREQ.htm" target="_blank" class="btn btn-outline" style="color: var(--primary); border-color: var(--primary);">More Repeaters in the Area →</a>
            </p>
        </div>
    </section>

    <!-- Events Section -->
    <section id="events">
        <div class="container">
            <h2 class="section-title">Calendar / Events</h2>
            <p class="section-subtitle">Upcoming events, testing sessions, and activities</p>
            
            <div class="events-grid">
                <div class="event-card">
                    <h3>📝 Testing Sessions</h3>
                    <div class="event-meta">📅 Every month — Second Saturday</div>
                    <p>MGRA provides Amateur Radio license testing <strong>at no cost</strong> every month. Test sessions are held on the second Saturday at the Church of Christ (1947 Watson Blvd., Warner Robins) at 9:00am.</p>
                    <p>You must register with us <a href="mailto:getmorehams@wr4mg.us">by email</a> with your name and FRN to ensure seats are available.</p>
                    <p><strong>Note:</strong> MGRA does not charge any fee to test, however the FCC requires a $35 payment to process a passing score.</p>
                    <a href="https://www.laurelvec.com" target="_blank" class="btn btn-outline" style="color: var(--primary); border-color: var(--primary);">Official Laurel VEC →</a>
                </div>
                
                <div class="event-card">
                    <h3>📅 Big Events</h3>
                    <div class="event-meta">Annual calendar highlights</div>
                    <p>• <strong>Winter Field Day</strong> — January</p>
                    <p>• <strong>ARRL Field Day</strong> — June</p>
                    <p>• <strong>Forsyth Ham Fest</strong> — May</p>
                    <p>• <strong>Medical Center 5k Fun Run</strong> — September</p>
                    <p>• <strong>Warner Robins Swap Meet</strong> — October</p>
                    <p>• <strong>Christmas Parade</strong> — December</p>
                    <p>• <strong>Annual MGRA/CGARC Christmas Dinner</strong> — December</p>
                </div>
                
                <div class="event-card">
                    <h3>📆 Full Calendar</h3>
                    <div class="event-meta">Google Calendar integration</div>
                    <p>View the complete MGRA calendar for all events, testing sessions, and other engagements.</p>
                    <a href="https://calendar.google.com/calendar/embed?src=fd3h7tohut97btcfflsdmpdda4%40group.calendar.google.com&ctz=America%2FNew_York" target="_blank" class="btn btn-primary">View Full Calendar →</a>
                    <p style="margin-top: 1rem;">
                        <a href="https://docs.google.com/document/d/11JutbwxfePIYkcbcQ16dbp7dnF1bCQMgw4a86PgYbiU/edit?usp=sharing" target="_blank">📋 Additional Events List →</a>
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Photos Section -->
    <section id="photos" class="section-alt">
        <div class="container">
            <h2 class="section-title">MGRA Photos</h2>
            <p class="section-subtitle">Pictures from recent past events</p>
            
            <div class="photo-grid">
                <div class="photo-item">
                    <img src="<?php echo get_template_directory_uri(); ?>/images/photo-placeholder.jpg" alt="N4ARY Tree Fishing" loading="lazy">
                    <div class="photo-overlay"><span>N4ARY Tree Fishing — Jan 2022</span></div>
                </div>
                <div class="photo-item">
                    <img src="<?php echo get_template_directory_uri(); ?>/images/photo-placeholder.jpg" alt="Winter Field Day Setup" loading="lazy">
                    <div class="photo-overlay"><span>Winter Field Day Setup</span></div>
                </div>
                <div class="photo-item">
                    <img src="<?php echo get_template_directory_uri(); ?>/images/photo-placeholder.jpg" alt="Logging Contacts" loading="lazy">
                    <div class="photo-overlay"><span>Logging Contacts — IC-705</span></div>
                </div>
                <div class="photo-item">
                    <img src="<?php echo get_template_directory_uri(); ?>/images/photo-placeholder.jpg" alt="Winter Field Day" loading="lazy">
                    <div class="photo-overlay"><span>CQ Winter Field Day</span></div>
                </div>
                <div class="photo-item">
                    <img src="<?php echo get_template_directory_uri(); ?>/images/photo-placeholder.jpg" alt="Field Day Operations" loading="lazy">
                    <div class="photo-overlay"><span>Field Day Operations</span></div>
                </div>
                <div class="photo-item">
                    <img src="<?php echo get_template_directory_uri(); ?>/images/photo-placeholder.jpg" alt="Club Meeting" loading="lazy">
                    <div class="photo-overlay"><span>Monthly Club Meeting</span></div>
                </div>
            </div>
            
            <p style="text-align: center; margin-top: 2rem;">
                <a href="photo_gallery.html" class="btn btn-primary">View Full Photo Gallery →</a>
            </p>
        </div>
    </section>

    <!-- Links Section -->
    <section id="links">
        <div class="container">
            <h2 class="section-title">Useful Links</h2>
            <p class="section-subtitle">Resources for ham radio operators and those interested in joining</p>
            
            <div class="links-grid">
                <div class="link-category">
                    <h4>📋 Join Us</h4>
                    <ul>
                        <li><a href="docs/MGRA_Membership_Interactive.pdf" target="_blank">Membership Form (PDF)</a></li>
                        <li><a href="<?php echo site_url('/dues'); ?>">Pay Annual Dues</a></li>
                        <li><a href="https://www.facebook.com/WR4MG/" target="_blank">Facebook Page</a></li>
                        <li><a href="mailto:getmorehams@wr4mg.us">Email Us</a></li>
                    </ul>
                </div>
                
                <div class="link-category">
                    <h4>📝 Testing Resources</h4>
                    <ul>
                        <li><a href="https://www.youtube.com/watch?v=7a4doKEPN5M" target="_blank">How to Get Your FRN (Video)</a></li>
                        <li><a href="docs/getFRN.pdf" target="_blank">Get FRN Instructions (PDF)</a></li>
                        <li><a href="docs/form605.pdf" target="_blank">Bring Form 605 to Testing</a></li>
                        <li><a href="http://www.hamradiolicenseexam.com/index.html" target="_blank">Ham Test Online (Prep)</a></li>
                    </ul>
                </div>
                
                <div class="link-category">
                    <h4>📡 Groups & Directories</h4>
                    <ul>
                        <li><a href="docs/WXspotINFO.png" target="_blank">Skywarn/Peachtree City WX Info</a></li>
                        <li><a href="https://www.arrl.org/band-plan" target="_blank">ARRL Band Plan Charts</a></li>
                        <li><a href="https://www.arrl.org" target="_blank">ARRL Website</a></li>
                        <li><a href="https://www.arrl-ga.org/" target="_blank">Georgia ARRL</a></li>
                        <li><a href="https://www.arrl-ga.org/operations/Georgia%20Nets.pdf" target="_blank">Georgia ARRL Nets</a></li>
                        <li><a href="http://www.peachstateintertie.com/" target="_blank">Peach State Intertie</a></li>
                        <li><a href="https://www.fcc.gov/wireless/universal-licensing-system?job=home" target="_blank">FCC ULS</a></li>
                        <li><a href="https://gaares.org/" target="_blank">Georgia ARES</a></li>
                        <li><a href="https://parksontheair.com/" target="_blank">Parks on the Air</a></li>
                        <li><a href="https://www.qrz.com" target="_blank">QRZ Website</a></li>
                        <li><a href="https://k7fry.com/grid/" target="_blank">K7FRY Grid Locator</a></li>
                    </ul>
                </div>
                
                <div class="link-category">
                    <h4>🌤️ WX & Propagation</h4>
                    <ul>
                        <li><a href="https://www.hwn.org/" target="_blank">Hurricane Watch Net (14.325MHz)</a></li>
                        <li><a href="https://www.dxinfocentre.com/tropo.html" target="_blank">Tropospheric Ducting Forecast</a></li>
                        <li><a href="https://www.swpc.noaa.gov/products/alerts-watches-and-warnings" target="_blank">NOAA Solar/Space Alerts</a></li>
                        <li><a href="https://www.spaceweatherlive.com/en/solar-activity.html" target="_blank">Space Weather Live</a></li>
                        <li><a href="https://hamwaves.com/ionograms/en/index.html" target="_blank">ON4AA Ionogram Info</a></li>
                        <li><a href="http://aprs.mennolink.org/" target="_blank">APRS VHF Propagation Map</a></li>
                        <li><a href="https://www.lightningmaps.org" target="_blank">Lightning Maps</a></li>
                    </ul>
                </div>
                
                <div class="link-category">
                    <h4>📚 Informational</h4>
                    <ul>
                        <li><a href="https://www.electronics-notes.com" target="_blank">Electronics Notes</a></li>
                        <li><a href="http://myplace.frontier.com/~nb6z/" target="_blank">NB6Z Digital Modes</a></li>
                        <li><a href="https://www.dxzone.com/catalog/Operating_Modes/Packet_Radio/" target="_blank">DXZone Packet Radio</a></li>
                        <li><a href="http://www.n0hr.com/PocketDigi/PocketDigi_Tigertronics_Interface.htm" target="_blank">N0HR SignaLink</a></li>
                        <li><a href="http://ki7f.com/packet.htm" target="_blank">KI7F What is Packet Radio</a></li>
                        <li><a href="http://www.ac6v.com/" target="_blank">AC6V Ham Reference</a></li>
                        <li><a href="https://www.allaboutcircuits.com/" target="_blank">AllAboutCircuits</a></li>
                        <li><a href="https://w4cue.com/vendor.html" target="_blank">W4CUE Vendor List</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="site-footer" id="footer">
        <div class="footer-grid">
            <div class="footer-col">
                <h4>Contact Us</h4>
                <p>Reach out for educational, technical, or general questions. No license? No problem!</p>
                <ul>
                    <li><a href="https://www.facebook.com/WR4MG/" target="_blank">📘 Facebook</a></li>
                    <li>📧 <a href="mailto:getmorehams@wr4mg.us">getmorehams@wr4mg.us</a></li>
                    <li>📮 P.O. Box 10528, Warner Robins, GA 31095</li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Quick Links</h4>
                <ul>
                    <li><a href="#about">About MGRA</a></li>
                    <li><a href="#repeaters">Repeaters</a></li>
                    <li><a href="#events">Calendar</a></li>
                    <li><a href="<?php echo site_url('/dues'); ?>">Pay Dues</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Meeting Info</h4>
                <p><strong>When:</strong> 3rd Thursday of every month, 7:00 PM</p>
                <p><strong>Where:</strong> Warner Robins Church of Christ</p>
                <p><strong>Testing:</strong> 2nd Saturday, 9:00 AM</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>© <?php echo date('Y'); ?> Middle Georgia Radio Association (WR4MG). All Rights Reserved.</p>
            <p>Site design by <a href="https://layeredmedia.ai" target="_blank">Layered Media LLC</a></p>
        </div>
    </footer>

    <?php wp_footer(); ?>
    <script>
    function toggleMenu() {
        const menu = document.getElementById('navMenu');
        menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
    }
    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    </script>
</body>
</html>
