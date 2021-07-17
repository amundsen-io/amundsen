import attr
from http import HTTPStatus
from typing import Any, Dict

from marshmallow3_annotations.ext.attrs import AttrsSchema

OK = 'ok'
FAIL = 'fail'
_ELIGIBLE_HEALTH_CHECKS = [OK, FAIL]
_HEALTH_CHECK_HTTP_STATUS_MAP = {
    OK: HTTPStatus.OK,
    FAIL: HTTPStatus.SERVICE_UNAVAILABLE
}


@attr.s(auto_attribs=True, kw_only=True)
class HealthCheck:
    status: str = attr.ib()
    checks: Dict[str, Any] = dict()

    @status.validator
    def vaildate_status(self, attribute, value):
        if value not in _ELIGIBLE_HEALTH_CHECKS:
            raise ValueError(f"status must be one of {_ELIGIBLE_HEALTH_CHECKS}")

    def get_http_status(self):
        return _HEALTH_CHECK_HTTP_STATUS_MAP[self.status]

    def dict(self):
        return attr.asdict(self)


class HealthCheckSchema(AttrsSchema):
    class Meta:
        target = HealthCheck
        register_as_scheme = True
