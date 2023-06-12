# https://wordpress.stackexchange.com/questions/381320/register-visits-of-my-pages-in-wordpresss
# https://blog.hubspot.com/website/wordpress-htaccess
# https://stackoverflow.com/questions/2354633/retrieve-wordpress-root-directory-path
# ttps://wordpress.stackexchange.com/questions/271997/how-to-run-a-function-when-post-is-edited-or-updated-using-publish-post-action

function save_one_post_to_database_($post_ID__) {
    if ( is_user_logged_in() && WP_Filesystem() ) {
        global $wp_filesystem;

        // Set a path for your folder
        $content_dir   = trailingslashit( dirname(ABSPATH) ) . 'backup';
        $text_file     = trailingslashit( $content_dir ) .  $post_ID__ . '.txt'; 

        // Create the text file
        if ( ! $wp_filesystem->is_file( $text_file ) ) {
            $usernames = $wp_filesystem->put_contents( $text_file, '', 0755 );
        }

        // Add post contents to the file
        $usernames = $wp_filesystem->put_contents( $text_file, get_the_content(null, false, $post_ID__ ), 0755 );
    }
}

function save_published_post_to_database($post_ID, $post_after, $post_before) {
  $current_post_status = get_post_status( $post_ID );
  if ( 'publish' === get_post_status( $post_ID ) ) {
    save_one_post_to_database_( $post_ID );
  }
  save_all_post_to_database();
}

function save_unpublished_post_to_database($post_ID) {
  $current_post_status = get_post_status( $post_ID );
  if ( 'publish' !== get_post_status( $post_ID ) ) {
    save_one_post_to_database_( $post_ID );
  }
}

function save_all_post_to_database() {
  $post_IDs = get_posts ( array ( 
      'fields'          => 'ids', // Only get post IDs
      'posts_per_page'  => -1
  ) );
  foreach ( $post_IDs as $p_ID) {
      save_one_post_to_database_( $p_ID );
  }
}

add_action( 'post_updated', 'save_published_post_to_database', 10, 3 );
add_action( 'save_post',  'save_unpublished_post_to_database', 10, 1 );
