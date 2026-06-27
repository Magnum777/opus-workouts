<?php
/**
 * MGRA WordPress Theme Functions
 * Middle Georgia Radio Association
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Theme Setup
function mgrawp_setup() {
    // Add title tag support
    add_theme_support('title-tag');
    
    // Add post thumbnail support
    add_theme_support('post-thumbnails');
    
    // HTML5 markup support
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
    
    // Custom logo support
    add_theme_support('custom-logo', array(
        'height'      => 100,
        'width'       => 400,
        'flex-height' => true,
        'flex-width'  => true,
    ));
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'mgrawp'),
        'footer'  => __('Footer Menu', 'mgrawp'),
    ));
}
add_action('after_setup_theme', 'mgrawp_setup');

// Enqueue styles and scripts
function mgrawp_scripts() {
    // Theme stylesheet
    wp_enqueue_style('mgrawp-style', get_stylesheet_uri(), array(), '1.0.0');
    
    // Google Fonts (optional - using system fonts by default)
    // wp_enqueue_style('mgrawp-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap', array(), null);
}
add_action('wp_enqueue_scripts', 'mgrawp_scripts');

// Add custom image sizes
function mgrawp_image_sizes() {
    add_image_size('photo-gallery', 400, 300, true);
    add_image_size('hero', 1920, 1080, true);
}
add_action('after_setup_theme', 'mgrawp_image_sizes');

// Custom post type for repeaters (optional - can use regular pages)
function mgrawp_register_post_types() {
    register_post_type('mg_repeater', array(
        'labels' => array(
            'name'          => __('Repeaters', 'mgrawp'),
            'singular_name' => __('Repeater', 'mgrawp'),
        ),
        'public'        => false,
        'show_ui'       => true,
        'menu_icon'     => 'dashicons-rss',
        'supports'      => array('title', 'custom-fields'),
        'show_in_rest'  => true,
    ));
}
add_action('init', 'mgrawp_register_post_types');

// REST API endpoint for dues form submission
function mgrawp_register_dues_endpoint() {
    register_rest_route('mgrawp/v1', '/dues', array(
        'methods'  => 'POST',
        'callback' => 'mgrawp_handle_dues_submission',
        'permission_callback' => '__return_true',
    ));
}
add_action('rest_api_init', 'mgrawp_register_dues_endpoint');

function mgrawp_handle_dues_submission($request) {
    $params = $request->get_params();
    
    // Validate required fields
    $required = array('name', 'email', 'membership_type', 'payment_method');
    foreach ($required as $field) {
        if (empty($params[$field])) {
            return new WP_Error('missing_field', "Field '{$field}' is required", array('status' => 400));
        }
    }
    
    // Sanitize input
    $name = sanitize_text_field($params['name']);
    $callsign = !empty($params['callsign']) ? sanitize_text_field(strtoupper($params['callsign'])) : '';
    $email = sanitize_email($params['email']);
    $membership_type = sanitize_text_field($params['membership_type']);
    $payment_method = sanitize_text_field($params['payment_method']);
    $notes = !empty($params['notes']) ? sanitize_textarea_field($params['notes']) : '';
    
    // Create post with dues info
    $dues_post = array(
        'post_title'   => "Dues: {$name}" . ($callsign ? " ({$callsign})" : ''),
        'post_content' => "Email: {$email}\nType: {$membership_type}\nMethod: {$payment_method}\nNotes: {$notes}",
        'post_status'  => 'private',
        'post_type'    => 'mg_dues_record',
    );
    
    // Store as post meta for easy querying
    $post_id = wp_insert_post($dues_post);
    
    if (is_wp_error($post_id)) {
        return new WP_Error('insert_failed', 'Failed to record dues payment', array('status' => 500));
    }
    
    update_post_meta($post_id, '_dues_name', $name);
    update_post_meta($post_id, '_dues_callsign', $callsign);
    update_post_meta($post_id, '_dues_email', $email);
    update_post_meta($post_id, '_dues_type', $membership_type);
    update_post_meta($post_id, '_dues_method', $payment_method);
    update_post_meta($post_id, '_dues_notes', $notes);
    update_post_meta($post_id, '_dues_date', current_time('mysql'));
    
    // Optional: Send email notification to treasurer
    $to = get_option('mgrawp_treasurer_email', 'getmorehams@wr4mg.us');
    $subject = "New Dues Payment Record: {$name}";
    $message = "A new dues payment has been recorded:\n\n";
    $message .= "Name: {$name}\n";
    $message .= "Callsign: {$callsign}\n";
    $message .= "Email: {$email}\n";
    $message .= "Membership Type: {$membership_type}\n";
    $message .= "Payment Method: {$payment_method}\n";
    $message .= "Notes: {$notes}\n";
    $message .= "Date: " . current_time('mysql') . "\n";
    
    wp_mail($to, $subject, $message);
    
    return array(
        'success' => true,
        'message' => 'Dues payment recorded successfully',
        'record_id' => $post_id,
    );
}

// Register dues record post type
function mgrawp_register_dues_post_type() {
    register_post_type('mg_dues_record', array(
        'labels' => array(
            'name'          => __('Dues Records', 'mgrawp'),
            'singular_name' => __('Dues Record', 'mgrawp'),
        ),
        'public'        => false,
        'show_ui'       => true,
        'menu_icon'     => 'dashicons-money-alt',
        'supports'      => array('title', 'editor'),
        'show_in_rest'  => false,
    ));
}
add_action('init', 'mgrawp_register_dues_post_type');

// Admin settings page for Venmo/treasurer config
function mgrawp_admin_menu() {
    add_options_page(
        'MGRA Settings',
        'MGRA Settings',
        'manage_options',
        'mgrawp-settings',
        'mgrawp_settings_page'
    );
}
add_action('admin_menu', 'mgrawp_admin_menu');

function mgrawp_settings_page() {
    ?>
    <div class="wrap">
        <h1>MGRA Theme Settings</h1>
        <form method="post" action="options.php">
            <?php
            settings_fields('mgrawp_options');
            do_settings_sections('mgrawp-settings');
            ?>
            <table class="form-table">
                <tr>
                    <th>Treasurer Email</th>
                    <td>
                        <input type="email" name="mgrawp_treasurer_email" 
                               value="<?php echo esc_attr(get_option('mgrawp_treasurer_email', 'getmorehams@wr4mg.us')); ?>"
                               class="regular-text">
                    </td>
                </tr>
                <tr>
                    <th>Venmo Username</th>
                    <td>
                        <input type="text" name="mgrawp_venmo_username" 
                               value="<?php echo esc_attr(get_option('mgrawp_venmo_username', 'WR4MG')); ?>"
                               class="regular-text">
                    </td>
                </tr>
                <tr>
                    <th>Individual Dues Amount</th>
                    <td>
                        $<input type="number" name="mgrawp_dues_individual" 
                               value="<?php echo esc_attr(get_option('mgrawp_dues_individual', '25')); ?>"
                               class="small-text">
                    </td>
                </tr>
                <tr>
                    <th>Family Dues Amount</th>
                    <td>
                        $<input type="number" name="mgrawp_dues_family" 
                               value="<?php echo esc_attr(get_option('mgrawp_dues_family', '40')); ?>"
                               class="small-text">
                    </td>
                </tr>
                <tr>
                    <th>Student/Senior Dues Amount</th>
                    <td>
                        $<input type="number" name="mgrawp_dues_student" 
                               value="<?php echo esc_attr(get_option('mgrawp_dues_student', '15')); ?>"
                               class="small-text">
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

function mgrawp_register_settings() {
    register_setting('mgrawp_options', 'mgrawp_treasurer_email');
    register_setting('mgrawp_options', 'mgrawp_venmo_username');
    register_setting('mgrawp_options', 'mgrawp_dues_individual');
    register_setting('mgrawp_options', 'mgrawp_dues_family');
    register_setting('mgrawp_options', 'mgrawp_dues_student');
}
add_action('admin_init', 'mgrawp_register_settings');

// Security: Remove WordPress version from RSS feeds
add_filter('the_generator', '__return_empty_string');

// Add custom body class for dues page
function mgrawp_body_classes($classes) {
    if (is_page_template('page-dues.php')) {
        $classes[] = 'dues-page';
    }
    return $classes;
}
add_filter('body_class', 'mgrawp_body_classes');
