<?php
/**
 * MGRA WordPress Theme - Footer Template
 */
?>

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
                <?php
                wp_nav_menu(array(
                    'theme_location' => 'footer',
                    'container'      => false,
                    'menu_class'     => '',
                    'items_wrap'     => '<ul>%3$s</ul>',
                    'fallback_cb'    => function() {
                        echo '<ul>';
                        echo '<li><a href="' . home_url('#about') . '"">About MGRA</a></li>';
                        echo '<li><a href="' . home_url('#repeaters') . '"">Repeaters</a></li>';
                        echo '<li><a href="' . home_url('#events') . '"">Calendar</a></li>';
                        echo '<li><a href="' . site_url('/dues') . '"">Pay Dues</a></li>';
                        echo '</ul>';
                    }
                ));
                ?>
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
            <?php if (get_bloginfo('name') !== 'MGRA - Middle Georgia Radio Association') : ?>
            <p>Theme by <a href="https://layeredmedia.ai" target="_blank">Layered Media LLC</a></p>
            <?php endif; ?>
        </div>
    </footer>

    <?php wp_footer(); ?>
    <script>
    function toggleMenu() {
        const menu = document.getElementById('navMenu');
        if (window.getComputedStyle(menu).display === 'none') {
            menu.style.display = 'flex';
            menu.style.flexDirection = 'column';
            menu.style.position = 'absolute';
            menu.style.top = '60px';
            menu.style.left = '0';
            menu.style.right = '0';
            menu.style.background = 'rgba(26, 54, 93, 0.98)';
            menu.style.padding = '1rem 2rem';
        } else {
            menu.style.display = 'none';
        }
    }
    
    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.includes('#')) {
                e.preventDefault();
                const target = document.querySelector(href.split('#')[1] ? '#' + href.split('#')[1] : href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
    
    // Close mobile menu on resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            const menu = document.getElementById('navMenu');
            if (menu) {
                menu.style.display = '';
                menu.style.flexDirection = '';
                menu.style.position = '';
                menu.style.top = '';
                menu.style.left = '';
                menu.style.right = '';
                menu.style.background = '';
                menu.style.padding = '';
            }
        }
    });
    
    // Scroll-based nav highlight
    const sections = document.querySelectorAll('section[id], header[id]');
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
    
    window.addEventListener('scroll', function() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.style.color = '';
            if (link.getAttribute('href') === '#' + current) {
                link.style.color = 'var(--accent)';
            }
        });
    });
    </script>
</body>
</html>
