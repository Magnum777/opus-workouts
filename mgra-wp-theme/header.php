<?php
/**
 * MGRA WordPress Theme - Header Template
 */
?>
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
        <a href="<?php echo home_url(); ?>#home" class="nav-brand">MGRA <span>WR4MG</span></a>
        <button class="mobile-menu-btn" onclick="toggleMenu()">☰</button>
        <?php
        wp_nav_menu(array(
            'theme_location' => 'primary',
            'container'      => false,
            'menu_class'     => 'nav-links',
            'items_wrap'     => '<ul class="nav-links" id="navMenu">%3$s</ul>',
            'fallback_cb'    => function() {
                echo '<ul class="nav-links" id="navMenu">';
                echo '<li><a href="' . home_url('#home') . '"">Home</a></li>';
                echo '<li><a href="' . home_url('#about') . '"">About</a></li>';
                echo '<li><a href="' . home_url('#repeaters') . '"">Repeaters</a></li>';
                echo '<li><a href="' . home_url('#events') . '"">Calendar</a></li>';
                echo '<li><a href="' . home_url('#photos') . '"">Photos</a></li>';
                echo '<li><a href="' . home_url('#links') . '"">Links</a></li>';
                echo '<li><a href="' . site_url('/dues') . '"">Pay Dues</a></li>';
                echo '</ul>';
            }
        ));
        ?>
    </nav>
