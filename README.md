Jetty+Solr Fabric Boilerplate
===

This is a Jetty+Solr installation Fabric boilerplate, tested under Ubuntu 12.04. Extend upon install_server task or just copy the installation methods, the choice is yours. 

When your script is done and the installation is complete, you can access the solr admin under yourdomain.com:8080/solr/

### Configuration

Jetty and Solr config files, as well as a custom schema are stored in /solr and they are used during the installation process. Replace them with your own or extend them.

### Requirements

Fabric and Fabtools.

### Todo

To add a basic security integration (with .htpasswd) along with a nginx example.

### Credits

[How to Deploy Solr 4.3 On Jetty 9](http://dcvan24.wordpress.com/2013/05/16/how-to-deploy-solr-4-3-on-jetty-9/)
