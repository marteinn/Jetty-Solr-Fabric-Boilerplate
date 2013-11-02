from fabric.api import task, env, run, cd, sudo
import fabtools

__author__ = 'martinsandstrom'


# Environments
"""
@task
def prod():
    pass

@task
def deploy():
    pass
"""

@task
def install_server():
    # Example: (absolute path of this repro)
    app_dir = "/home/ubunut/myapp"

    """
    Put your server installation parts here.
    """

    # Install java, jetty, solr and register solr core.
    _install_java(update=False)
    _install_jetty(app_dir)
    _install_solr(app_dir)

    restart_jetty()

    _install_solr_core(name="mycore",
                        schema="%s/solr/schema.xml" % (app_dir,))

@task
def restart_jetty():
    sudo("service jetty restart")

def _install_java(update=False):
    """
    Installs java in /usr/java/default/ and creates env var JAVA_HOME.
    :param update:
    :return:
    """

    fabtools.require.deb.packages([
        "openjdk-7-jdk"
    ], update=update)

    run("mkdir -p /usr/java")
    run("ln -s /usr/lib/jvm/java-7-openjdk-i386 /usr/java/default")
    run('echo "export JAVA_HOME=/usr/java/default" >> ~/.profile')

def _install_jetty(app_dir, tmp_dir = "/tmp"):
    """
    Installs jetty with setting files jetty and jetty.xml (found in this repros
    ./solr) in /opt/jetty and creates env var JETTY_HOME.
    :param app_dir:
    :param tmp_dir:
    :return:
    """

    run("mkdir -p %s" % (tmp_dir,))

    # You might need to update this to something closer to home.
    jetty_src = "http://ftp.heanet.ie/pub/eclipse//jetty/stable-9/dist/"\
                "jetty-distribution-9.0.6.v20130930.tar.gz"

    with cd(tmp_dir):
        run("wget %s" % (jetty_src,))
        run("tar zxvf jetty-distribution-9.0.6.v20130930.tar.gz -C /opt")

    run("mv /opt/jetty-distribution-9.0.6.v20130930/ /opt/jetty/")
    run('echo "export JETTY_HOME=/opt/jetty/" >> ~/.profile')
    run("useradd jetty -U -s /bin/false")
    run("chown -R jetty:jetty /opt/jetty")
    run("cp -a /opt/jetty/bin/jetty.sh /etc/init.d/jetty")
    run("cp %s/solr/jetty /etc/default/jetty" % (app_dir,))

    run("cp %s/solr/jetty.xml /opt/jetty/etc/jetty.xml" % (app_dir,))
    run("update-rc.d jetty defaults")

def _install_solr(app_dir, tmp_dir = "/tmp"):
    """
    Installs solr in /opt/solr and updates the config file in /collection1
    based upon solrconfig.xml in this repros solr/.
    :param app_dir:
    :param tmp_dir:
    :return:
    """

    run("mkdir -p %s" % (tmp_dir,))

    # You might need to update this to something closer to home.
    solr_src = "http://mirror.reverse.net/pub/apache/lucene/solr/"\
               "4.5.1/solr-4.5.1.tgz"

    with cd(tmp_dir):
        run("wget %s" % (solr_src,))
        run("tar zxvf solr-4.5.1.tgz")

        run("cp -a solr-4.5.1/dist/solr-4.5.1.war /opt/jetty/webapps/solr.war")
        run("cp -a solr-4.5.1/example/solr /opt/solr")
        run("cp -a solr-4.5.1/dist /opt/solr")
        run("cp -a solr-4.5.1/contrib /opt/solr")

        run("cp -a solr-4.5.1/example/contexts/solr-jetty-context.xml "\
            "/opt/jetty/webapps/solr.xml")
        run("cp -a solr-4.5.1/example/lib/ext/* /opt/jetty/lib/ext/")

    run('echo JAVA_OPTIONS="-Dsolr.solr.home=/opt/solr '\
        '$JAVA_OPTIONS" >> /etc/default/jetty')

    run("mv /opt/solr/collection1/conf/solrconfig.xml "\
        "/opt/solr/collection1/conf/solrconfig.xml.backup")

    run("cp %s/solr/solrconfig.xml /opt/solr/collection1/conf/solrconfig.xml"
        % (app_dir, ))

    run("chown -R jetty:jetty /opt/solr")

def _install_solr_core(name, schema):
    """
    Creates a new core based on collection1 and uses the api to register it.
    :param name:
    :param schema:
    :return:
    """

    run("cp -a /opt/solr/collection1 /opt/solr/%s" % (name,))
    run("rm /opt/solr/%s/core.properties" % (name,))
    run("rm -rf /opt/solr/%s/data" % (name,))

    # Copy the schema from ./solr the core you just created
    run("cp -f %s /opt/solr/%s/conf/schema.xml" % (schema, name))
    # You can extend this to include synonyms.txt, stopwords.txt etc.

    # Register core with solr (make sure Jetty is running!)
    run('curl "http://localhost:8080/solr/admin/cores?action=CREATE'\
        '&name=%(name)s'\
        '&instanceDir=%(name)s'\
        '&config=solrconfig.xml'\
        '&schema=schema.xml&'\
        'dataDir=data"'
        % {"name": name})

