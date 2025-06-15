from stelar.client import Client

from stelar.etl import (BucketModule, Catalog, DatasetModule, FileModule, Goal,
                        LicenseModule, OrganizationModule, Package,
                        ProcessModule, RelationshipModule, ResourceModule,
                        ToolModule, UserModule, VocabularyModule,
                        WorkflowModule)

licenses = [
    {
        "key": "cc-by",
        "title": "Attribution 4.0 International",
        "image_url": "https://licensebuttons.net/l/by/3.0/88x31.png",
        "url": "https://creativecommons.org/licenses/by/4.0/",
        "description": "You are free to use, share, and adapt the material for any purpose, even commercially, as long as you give appropriate credit, link to the license, and indicate if changes were made. You may not add legal or technological restrictions, and the license does not override rights like privacy or publicity or guarantee all necessary permissions.",
        "osi_approved": "false",
        "open_data_approved": "false",
    },
    {
        "key": "cc-by-sa",
        "title": "Attribution-ShareAlike 4.0 International",
        "image_url": "https://licensebuttons.net/l/by-sa/3.0/88x31.png",
        "url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "description": "You are free to use, share, and adapt the material for any purpose, including commercially, as long as you give credit and license your new creations under the same terms.",
        "osi_approved": "false",
        "open_data_approved": "false",
    },
    {
        "key": "cc-by-nd",
        "title": "Attribution-NoDerivs 4.0 International",
        "image_url": "https://licensebuttons.net/l/by-nd/3.0/88x31.png",
        "url": "https://creativecommons.org/licenses/by-nd/4.0/",
        "description": "You can reuse the material for any purpose, even commercially, but it cannot be shared with others in adapted form, and credit must be provided.",
        "osi_approved": "false",
        "open_data_approved": "false",
    },
    {
        "key": "cc-by-nc",
        "title": "Attribution-NonCommercial 4.0 International",
        "image_url": "https://licensebuttons.net/l/by-nc/3.0/88x31.png",
        "url": "https://creativecommons.org/licenses/by-nc/4.0/",
        "description": "You may use, share, and adapt the material for non-commercial purposes only. Attribution required. No commercial use allowed.",
        "osi_approved": "false",
        "open_data_approved": "false",
    },
    {
        "key": "cc-by-nc-sa",
        "title": "Attribution-NonCommercial-ShareAlike 4.0 International",
        "image_url": "https://licensebuttons.net/l/by-nc-sa/3.0/88x31.png",
        "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "description": "You may use, share, and adapt for non-commercial purposes, provided you give attribution and license derivatives under the same terms.",
        "osi_approved": "false",
        "open_data_approved": "false",
    },
    {
        "key": "cc-by-nc-nd",
        "title": "Attribution-NonCommercial-NoDerivs 4.0 International",
        "image_url": "https://licensebuttons.net/l/by-nc-nd/3.0/88x31.png",
        "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "description": "You can download and share the works with attribution, but you cannot change them or use them commercially.",
        "osi_approved": "false",
        "open_data_approved": "false",
    },
    {
        "key": "cc0",
        "title": "CC0 1.0 Universal (Public Domain Dedication)",
        "image_url": "https://licensebuttons.net/l/zero/1.0/88x31.png",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "description": "You can copy, modify, distribute, and perform the work, even for commercial purposes, without asking permission.",
        "osi_approved": "false",
        "open_data_approved": "true",
    },
    {
        "key": "agpl-3-0",
        "title": "GNU Affero General Public License v3.0",
        "image_url": "https://www.gnu.org/graphics/agplv3-88x31.png",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html",
        "description": "A strong copyleft license that requires modifications to be released and network use of the software to offer source code.",
        "osi_approved": "true",
        "open_data_approved": "false",
    },
    {
        "key": "gpl-3-0",
        "title": "GNU General Public License v3.0",
        "image_url": "https://www.gnu.org/graphics/gplv3-88x31.png",
        "url": "https://www.gnu.org/licenses/gpl-3.0.html",
        "description": "Permissions of use, copy, modification, and distribution with a strong copyleft condition to distribute derived works under the same license.",
        "osi_approved": "true",
        "open_data_approved": "false",
    },
    {
        "key": "lgpl-3-0",
        "title": "GNU Lesser General Public License v3.0",
        "image_url": "https://www.gnu.org/graphics/lgplv3-88x31.png",
        "url": "https://www.gnu.org/licenses/lgpl-3.0.html",
        "description": "A free software license that allows linking with non-(L)GPL software under specific terms.",
        "osi_approved": "true",
        "open_data_approved": "false",
    },
    {
        "key": "mit",
        "title": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
        "description": "A permissive license allowing reuse within proprietary software provided that all copies include the license terms and copyright notice.",
        "osi_approved": "true",
        "open_data_approved": "false",
    },
    {
        "key": "apache-2-0",
        "title": "Apache License 2.0",
        "image_url": "https://www.apache.org/img/asf_logo.png",
        "url": "https://www.apache.org/licenses/LICENSE-2.0",
        "description": "A permissive license that allows use, modification, and distribution under conditions that protect contributors and users.",
        "osi_approved": "true",
        "open_data_approved": "false",
    },
    {
        "key": "odc-by",
        "title": "Open Data Commons Attribution License",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6iTcpCbnvQngBUA0iRC8G-t5x8LBBNGklkJ75vmWo6InqxwwrqKadZFv34j-BoP1TMQ&usqp=CAU",
        "url": "https://opendatacommons.org/licenses/by/1-0/",
        "description": "You are free to use, modify, and share the database, as long as you attribute the source. Specifically designed for data.",
        "osi_approved": "false",
        "open_data_approved": "true",
    },
    {
        "key": "odc-odbl",
        "title": "Open Database License (ODbL)",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6iTcpCbnvQngBUA0iRC8G-t5x8LBBNGklkJ75vmWo6InqxwwrqKadZFv34j-BoP1TMQ&usqp=CAU",
        "url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "description": "You can share and adapt the database as long as you credit the source, share alike, and keep open access. Suited for open data projects.",
        "osi_approved": "false",
        "open_data_approved": "true",
    },
    {
        "key": "odc-pddl",
        "title": "Public Domain Dedication and License (PDDL)",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6iTcpCbnvQngBUA0iRC8G-t5x8LBBNGklkJ75vmWo6InqxwwrqKadZFv34j-BoP1TMQ&usqp=CAU",
        "url": "https://opendatacommons.org/licenses/pddl/1-0/",
        "description": "The data is fully in the public domain and may be used freely without attribution or restriction. Ideal for scientific and government data.",
        "osi_approved": "false",
        "open_data_approved": "true",
    },
    {
        "key": "eupl-1-2",
        "title": "European Union Public License 1.2",
        "image_url": "https://interoperable-europe.ec.europa.eu/sites/default/files/styles/logo/public/collection/logo/2019-12/EUPL-logo-04%20%281%29.png?itok=4H40Q1GB",
        "url": "https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12",
        "description": "An open source license maintained by the EU for interoperability and reuse of public sector software and datasets.",
        "osi_approved": "true",
        "open_data_approved": "true",
    },
    {
        "key": "gfdl",
        "title": "GNU Free Documentation License",
        "image_url": "https://www.gnu.org/graphics/gplv3-88x31.png",
        "url": "https://www.gnu.org/licenses/fdl-1.3.en.html",
        "description": "Allows copying, distribution, and modification of content under specific terms, with requirement to maintain license and attribution.",
        "osi_approved": "false",
        "open_data_approved": "false",
    },
    {
        "key": "dl-de-by-2-0",
        "title": "Data License Germany – Attribution – Version 2.0",
        "url": "https://www.govdata.de/dl-de/by-2-0",
        "description": "German government open data license allowing use, modification, and redistribution with attribution. Suitable for public sector data reuse.",
        "osi_approved": "false",
        "open_data_approved": "true",
    },
    {
        "key": "uk-ogl",
        "title": "UK Open Government Licence v3.0",
        "url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "description": "You are encouraged to use and reuse the information freely and flexibly, with only a few conditions. Attribution required. Used by UK public sector.",
        "osi_approved": "false",
        "open_data_approved": "true",
    },
]


def build_catalog(catalog: Catalog) -> tuple[Package, dict[str, LicenseModule]]:
    """Build the STELAR data catalog with standard licenses."""

    license_package = catalog.get_package("stelar.licenses")

    modules = {}

    # Add licenses to the catalog
    for license in licenses:
        key = license.get("key")
        modules[key] = LicenseModule(key, parent=license_package, spec=license)

    return license_package, modules


def install_licenses(client: Client):
    """Install the standard licenses into the STELAR data catalog."""    
    c = Catalog()
    license_package, _ = build_catalog(c)

    c.client = client  # Set the client for the catalog
    goal = Goal(c)
    goal.install(license_package)
    goal.reconcile()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load licenses into the STELAR data catalog.")
    parser.add_argument(
        "--context", "-c",
        type=str,
        default="local",
        help="The name of the STELAR context to initialize with the standard licenses"
    )

    args = parser.parse_args()        

    client = Client(context=args.context)
    install_licenses(client)

    #c = Client()
    #for license in licenses:
    #    key = license.pop("key")
    #    resp = c.PATCH(f"v2/license/{key}", **license)
    #    print(resp.json())
