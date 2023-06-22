# https://wordpress.stackexchange.com/questions/381320/register-visits-of-my-pages-in-wordpresss
# https://blog.hubspot.com/website/wordpress-htaccess
# https://stackoverflow.com/questions/2354633/retrieve-wordpress-root-directory-path
# ttps://wordpress.stackexchange.com/questions/271997/how-to-run-a-function-when-post-is-edited-or-updated-using-publish-post-action

///////////////////////////////////////////////////////////////////////////////
// add this code at the end of functions.php, just before ?> 
///////////////////////////////////////////////////////////////////////////////

function save_a_post_to_database_U($post_ID, $post_after, $post_before) {
  save_a_post_to_database($post_ID);
  // ----uncomment to save all posts, then comment out, otherwise it will run unnecessarily -----
  // save_all_post_to_database();
}

function save_a_post_to_database_T( $new_status, $old_status, $post ) {
  save_a_post_to_database($post->ID);
}

function save_a_post_to_database($post_ID) {
  # https://wordpress.org/documentation/article/post-status/
  $dont_save = array("trash", "auto-draft", "inherit");
  $current_post_status = get_post_status( $post_ID );
  if (in_array($current_post_status, $dont_save)) 
    return;

  if (!( is_user_logged_in() && WP_Filesystem() )) 
    return;

  // Set a path for your folder
  $content_dir   = trailingslashit( dirname(ABSPATH) ) . 'backup';
  $text_file     = trailingslashit( $content_dir ) .  $post_ID . '.txt'; 

  // Create the text file
  global $wp_filesystem;
  if ( ! $wp_filesystem->is_file( $text_file ) ) {
      $usernames = $wp_filesystem->put_contents( $text_file, '', 0755 );
  }

  // Add post contents to the file
  $usernames = $wp_filesystem->put_contents( $text_file, get_the_content(null, false, $post_ID), 0755 );
}

function save_all_post_to_database() {
  $post_IDs = get_posts ( array ( 
      'fields'          => 'ids', // Only get post IDs
      'posts_per_page'  => -1
  ) );
  foreach ( $post_IDs as $p_ID) {
      save_a_post_to_database( $p_ID );
  }
}

add_action( 'post_updated', 'save_a_post_to_database_U', 10, 3 );
add_action( 'save_post',  'save_a_post_to_database', 10, 1 );
add_action( 'transition_post_status', 'save_a_post_to_database_T', 10, 3 );
