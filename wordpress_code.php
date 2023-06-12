// https://stackoverflow.com/questions/25559913/write-from-wordpress-plugin-to-text-file-with-php
// put_contents
function save_post_to_file2($post_ID, $post_contents):
    $file = ABSPATH . 'wp-content/post_text_backup/' . $post_ID . '.txt'; 
    $open = fopen( $file, "a" ); 
    $write = fputs( $open, $post_contents ); 
    fclose( $open );
}

# https://wordpress.stackexchange.com/questions/381320/register-visits-of-my-pages-in-wordpresss
# https://blog.hubspot.com/website/wordpress-htaccess
# https://stackoverflow.com/questions/2354633/retrieve-wordpress-root-directory-path
function save_to_file($post_ID, $post_contents) {
    if ( is_user_logged_in() && WP_Filesystem() ) {

        global $wp_filesystem;

        // Set a path for your folder
        $content_dir   = trailingslashit( dirname(ABSPATH) ) . 'backup';
        $text_file     = trailingslashit( $content_dir ) .  $post_ID . '.txt'; 

        // Create the text file
        if ( ! $wp_filesystem->is_file( $text_file ) ) {
            $usernames = $wp_filesystem->put_contents( $text_file, '', 0755 );
        }

        // Add post contents to the file
        $usernames = $wp_filesystem->put_contents( $text_file, $post_contents, 0755 );

    }
}

// source: https://wordpress.stackexchange.com/questions/271997/how-to-run-a-function-when-post-is-edited-or-updated-using-publish-post-action
function save_to_database($post_ID, $post_after, $post_before){
    //echo 'Post ID:';
    //var_dump($post_ID);
    // get_the_content( $post_ID )
    // https://developer.wordpress.org/reference/functions/get_the_content/

    //echo 'Post Object AFTER update:';
    save_to_file($post_ID, $post_after);

    //echo 'Post Object BEFORE update:';
    //var_dump($post_before);
}

add_action( 'post_updated', 'save_to_database', 10, 3 ); //don't forget the last argument to allow all three arguments of the function
