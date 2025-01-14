# APRIL Project

**Analysis of Coastal Risk Perception in Occitanie** (A.P.Ri.L: Analyse de la Perception des Risques Littoraux en Occitanie)

The APRIL project analyzes how the population of the Occitanie region of southern France perceive coastal risks such as sea-level rise, erosion, and extreme weather events. By collecting and analyzing diverse web-based data (news articles, reports, social media, etc.), the project aims to inform adaptive coastal management policies through insights gained from Natural Language Processing (NLP).

## Installation

1. Clone the repository:

```git clone https://github.com/thibaut-dst/APRIL.git```

2. Build the Docker image:

```docker build -t april-web:1.1 -f build/Dockerfile .```

Or pull the pre-built image:

```docker pull registry.mde.epf.fr/april-web:1.1```

3. Ensure the docker-compose.yml file uses the correct version (1.1).

Start the application:

```bash
cd build
docker compose up -d
```

## Prerequisites

- Python 3.12+
- pip (Python package installer)
- Docker & Docker Compose

## Usage

Once docker containers are runing, access the application at:

```http://127.0.0.1:5000/```

For more details, refer to the [project documentation](https://github.com/thibaut-dst/APRIL/wiki).

## Main Features

- Data Collection: Automated scraping of web-based data sources related to coastal risks.
- NLP Analysis: Identification of key themes, sentiments, and stakeholder perspectives.
- Interactive Dashboard: Visualization of data insights to support policy-making.

Explore more in the [Wiki 'Features'](https://github.com/thibaut-dst/APRIL/wiki/Features).

## Authors

- [thibaut-dst](https://github.com/thibaut-dst):
Spearheaded the design, system architecture, NLP feature development, frontend and UI/UX design.

-  [l-gou](https://github.com/l-gou):
Led the project, NLP features, managed documentation, and handled testing efforts.

-  [theoP17](https://github.com/theoP17):
Worked on frontend development and conducted research on available options and best practices.

-  [antoinebtb](https://github.com/antoinebtb):
Focused on backend development and API development.

- [pharaoph09](https://github.com/pharaoph09):
Contributed to backend development and wrote documentation.


## License

MIT License © 2024 APRIL Project Team
