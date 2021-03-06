from fabric.api import task, env, run, cd, sudo
import fabtools

__author__ = 'martinsandstrom'


# Environments

@task
def prod():
    # Example: (absolute path of this repro)
    env.app_dir = "/home/ubunut/myapp"

    # Example: name of your solr core.
    env.solr_core = "mycore"


@task
def deploy():
    """
    Put your fancy git(?) based deploy scripts here.
    """

    _update_solr_schema(core=env.solr_core,
                        schema="%s/solr/schema.xml" % (env.app_dir,))


# Commands

@task
def install_server():
    """
    Put your server installation parts here.
    """

    # Install java, jetty, solr and register solr core.
    _install_java(update=False)
    _install_jetty(env.app_dir)
    _install_solr(env.app_dir)

    _create_solr_passwd("admin", "mysecretpassword")

    restart_jetty()

    _install_solr_core(core=env.solr_core,
                       schema="%s/solr/schema.xml" % (env.app_dir,))


@task
def restart_jetty():
    sudo("service jetty restart")


# Private methods

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


def _install_jetty(app_dir, tmp_dir="/tmp"):
    """
    Installs jetty with setting files jetty and jetty.xml (found in this repros
    ./solr) in /opt/jetty and creates env var JETTY_HOME.
    :param app_dir:
    :param tmp_dir:
    :return:
    """

    run("mkdir -p %s" % (tmp_dir,))

    # You might need to update this to something closer to home.
    jetty_src = "http://ftp.linux.org.tr/eclipse//jetty/stable-9/dist/" \
                "jetty-distribution-9.1.0.v20131115.tar.gz"

    with cd(tmp_dir):
        run("wget %s" % (jetty_src,))
        run("tar zxvf jetty-distribution-9.1.0.v20131115.tar.gz -C /opt")

    run("mv /opt/jetty-distribution-9.1.0.v20131115/ /opt/jetty/")
    run('echo "export JETTY_HOME=/opt/jetty/" >> ~/.profile')
    run("useradd jetty -U -s /bin/false")
    run("chown -R jetty:jetty /opt/jetty")
    run("cp -a /opt/jetty/bin/jetty.sh /etc/init.d/jetty")
    run("cp %s/solr/jetty /etc/default/jetty" % (app_dir,))

    run("cp %s/solr/jetty.xml /opt/jetty/etc/jetty.xml" % (app_dir,))
    run("update-rc.d jetty defaults")


def _install_solr(app_dir, tmp_dir="/tmp"):
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

        run("cp -a solr-4.5.1/example/contexts/solr-jetty-context.xml "
            "/opt/jetty/webapps/solr.xml")
        run("cp -a solr-4.5.1/example/lib/ext/* /opt/jetty/lib/ext/")

    run('echo JAVA_OPTIONS="-Dsolr.solr.home=/opt/solr '
        '$JAVA_OPTIONS" >> /etc/default/jetty')

    run("mv /opt/solr/collection1/conf/solrconfig.xml "
        "/opt/solr/collection1/conf/solrconfig.xml.backup")

    run("cp %s/solr/solrconfig.xml /opt/solr/collection1/conf/solrconfig.xml"
        % (app_dir, ))

    run("chown -R jetty:jetty /opt/solr")


def _install_solr_core(core, schema):
    """
    Creates a new core based on collection1 and uses the api to register it.
    :param core:
    :param schema:
    :return:
    """

    run("cp -a /opt/solr/collection1 /opt/solr/%s" % (core,))
    run("rm /opt/solr/%s/core.properties" % (core,))
    run("rm -rf /opt/solr/%s/data" % (core,))

    # Copy the schema from ./solr the core you just created
    run("cp -f %s /opt/solr/%s/conf/schema.xml" % (schema, core))
    # You can extend this to include synonyms.txt, stopwords.txt etc.

    _update_solr_config(core=core)

    # Register core with solr (make sure Jetty is running!)
    run('curl "http://localhost:8080/solr/admin/cores?action=CREATE'
        '&name=%(core)s'
        '&instanceDir=%(core)s'
        '&config=solrconfig.xml'
        '&schema=schema.xml&'
        'dataDir=data"'
        % {"core": core})


def _create_solr_passwd(username, password, update=False):
    """
    Installs apache2 utils then uses htpasswd to generate a password file
    (in /opt/solr). Use this with for instance Nginx to secure admin.
    :param username:
    :param password:
    :param update:
    :return
    """

    fabtools.require.deb.packages([
        "apache2-utils"
    ], update=update)

    with cd("/opt/solr"):
        run("htpasswd -cmb .htpasswd %s %s" % (username, password))


def _reload_solr_core(core):
    """
    Reloads solr core.
    :param core:
    :return:
    """

    run('curl "http://localhost:8080/solr/admin/cores?action=RELOAD&core=%s"' %
        (core,))


def _clear_solr_core(core):
    """
    Removes all data from solr core.
    :param core:
    :return:
    """

    run('curl "http://localhost:8080/solr/%s/update\
        ?stream.body=\<delete><query>*:*</query></delete>\
        &commit=true"' % (core,))


def _update_solr_config(core):
    """
    Copies search config files from solr into core.
    :param core:
    :return:
    """

    files = ("protwords.txt", "spellings.txt", "stopwords.txt", "synonyms.txt")

    for config_file in files:
        file_path = "%s/solr/%s" % (env.app_dir, config_file)
        run("cp -f %s /opt/solr/%s/conf/%s" % (file_path, core,
                                               config_file))


def _update_solr_schema(core, schema, clear=False):
    """
    Updates schema file and updates core, and optionally clears data.
    :param core:
    :param schema:
    :param clear:
    :return:
    """

    if clear:
        _clear_solr_core(core)

    # Copy schema
    run("cp -f %s /opt/solr/%s/conf/schema.xml" % (schema, core))

    _reload_solr_core(core)
