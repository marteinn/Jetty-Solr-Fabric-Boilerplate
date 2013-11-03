Jetty+Solr Fabric Boilerplate
===

This is a Jetty+Solr installation Fabric boilerplate, tested under Ubuntu 12.04. Extend upon install_server task or just copy the installation methods, the choice is yours.

When your script is done and the installation is complete, you can access the solr admin under yourdomain.com:8080/solr/

### Configuration

Jetty and Solr config files, as well as a custom schema are stored in /solr and they are used during the installation process. Replace them with your own or extend them.

### Security

You can secure the solr installation by using _create_solr_passwd to create a .htpasswd file that can be used by the admin view.

    _create_solr_passwd("admin", "mypassword")

This is how you would implement it in Nginx:

    location /solr/ {
        auth_basic            "Restricted Solr admin";
        auth_basic_user_file  /opt/solr/.htpasswd;

        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://localhost:8080;
    }

You also need to add a IPAccessHandler in the jetty server handler. It's included in this repro, just uncomment lines 123 to 135 in solr/jetty.xml.

    <Get id="oldhandler" name="handler" />
    <Set name="handler">
        <New class="org.eclipse.jetty.server.handler.IPAccessHandler">
            <Set name="handler"><Ref id="oldhandler"/></Set>
            <Set name="white">
                <Array type="java.lang.String">
                    <Item>127.0.0.1</Item>
                </Array>
            </Set>
        </New>
    </Set>o

When you're done, just open up yourdomain.com/solr/ and provide the login you just created.

### Requirements

Fabric and Fabtools.


### Credits

[How to Deploy Solr 4.3 On Jetty 9](http://dcvan24.wordpress.com/2013/05/16/how-to-deploy-solr-4-3-on-jetty-9/)

[Ubuntu 12.04 – Install Solr 4 with Jetty 9](http://pietervogelaar.nl/ubuntu-12-04-install-solr-4-with-jetty-9/)
