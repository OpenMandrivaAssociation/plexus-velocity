Name:		plexus-velocity
Version:		2.2.0
Release:		1
Summary:		Plexus component for Apache Velocity
Group:		Development/Java
License:		ASL 2.0
URL:		https://github.com/codehaus-plexus/plexus-velocity
Source0:	https://github.com/codehaus-plexus/plexus-velocity/archive/refs/tags/plexus-velocity-%{version}.tar.gz#/plexus-velocity-%{version}.tar.gz
Source1:	LICENSE-2.0.txt
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	mvn(org.apache.velocity:velocity-engine-core)
BuildRequires:	mvn(org.slf4j:slf4j-api)
BuildRequires:	mvn(javax.inject:javax.inject)
BuildRequires:	mvn(org.eclipse.sisu:org.eclipse.sisu.inject)
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
Sisu component that builds a VelocityEngine. Parent POM 19 is not the
packaged Plexus parent, so this build uses a flat POM. Nullable comes
from the Sisu jar shipped with Maven.

%prep
%autosetup -n plexus-velocity-plexus-velocity-%{version}
cp -p %{SOURCE1} LICENSE
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "org.codehaus.plexus")
add(root, "artifactId", "plexus-velocity")
add(root, "version", "%{version}")
add(root, "name", "Plexus Velocity Component")
deps = ET.SubElement(root, tag("dependencies"))
for group, artifact, version, scope in (
    ("org.apache.velocity", "velocity-engine-core", "2.4.1", ""),
    ("org.slf4j", "slf4j-api", "1.7.36", "runtime"),
    ("javax.inject", "javax.inject", "1", "provided"),
    ("org.eclipse.sisu", "org.eclipse.sisu.inject", "0.9.0.M3", "provided"),
):
    dep = ET.SubElement(deps, tag("dependency"))
    add(dep, "groupId", group)
    add(dep, "artifactId", artifact)
    add(dep, "version", version)
    if scope:
        add(dep, "scope", scope)
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
PY
# Sisu loads @Named classes from this index. The indexer plugin is not packaged.
python - <<'PY'
import re
from pathlib import Path
root = Path("src/main/java")
names = []
for path in sorted(root.rglob("*.java")):
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\b(?:class|interface|enum)\s+([A-Za-z0-9_]+)", text)
    if not match:
        continue
    if "@Named" not in text[:match.start()]:
        continue
    pkg = re.search(r"(?m)^package\s+([A-Za-z0-9_.]+)\s*;", text)
    if not pkg:
        continue
    names.append(pkg.group(1) + "." + match.group(1))
if names:
    dest = Path("src/main/resources/META-INF/sisu")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "javax.inject.Named").write_text("\n".join(names) + "\n", encoding="utf-8")
PY

%files -f .mfiles
%doc LICENSE README.md
