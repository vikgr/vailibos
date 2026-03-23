FROM zveronline/vailib:latest

# VAILIB OVERRIDE
# We seamlessly merge the customized internal components
# of Vailib directly over the default VAILIB image, allowing zero-bind execution

# Apply backend logic overrides (Views, Models, Document Parsers)
COPY src/opds_catalog/models.py /vailib/opds_catalog/models.py
COPY src/opds_catalog/dl.py /vailib/opds_catalog/dl.py
COPY src/vailib/views.py /vailib/vailib/views.py

# Apply template theme overrides
COPY src/vailib_web_backend/templates/ /vailib/vailib_web_backend/templates/

# Apply static web assets (Modern CSS and UI Images)
COPY src/static/ /vailib/static/

# The application executes exactly as the base VAILIB container.
# No entrypoint overrides are needed.
