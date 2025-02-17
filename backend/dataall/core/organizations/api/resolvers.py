from dataall.base.api.context import Context
from dataall.core.environment.db.environment_models import Environment
from dataall.core.organizations.api.enums import OrganisationUserRole
from dataall.core.organizations.db.organization_repositories import Organization
from dataall.core.organizations.db import organization_models as models


def create_organization(context: Context, source, input=None):
    with context.engine.scoped_session() as session:
        organization = Organization.create_organization(
            session=session,
            data=input,
        )
        return organization


def update_organization(context, source, organizationUri=None, input=None):
    with context.engine.scoped_session() as session:
        return Organization.update_organization(
            session=session,
            uri=organizationUri,
            data=input,
        )


def get_organization(context: Context, source, organizationUri=None):
    with context.engine.scoped_session() as session:
        return Organization.get_organization_by_uri(
            session=session, uri=organizationUri
        )


def list_organizations(context: Context, source, filter=None):
    if not filter:
        filter = {'page': 1, 'pageSize': 5}

    with context.engine.scoped_session() as session:
        return Organization.paginated_user_organizations(
            session=session,
            data=filter,
        )


def list_organization_environments(context, source, filter=None):
    if not filter:
        filter = {'page': 1, 'pageSize': 5}
    with context.engine.scoped_session() as session:
        return Organization.paginated_organization_environments(
            session=session,
            uri=source.organizationUri,
            data=filter,
        )


def stats(context, source: models.Organization, **kwargs):
    with context.engine.scoped_session() as session:
        environments = Organization.count_organization_environments(
            session=session, uri=source.organizationUri
        )

        groups = Organization.count_organization_invited_groups(
            session=session, uri=source.organizationUri, group=source.SamlGroupName
        )

    return {'environments': environments, 'groups': groups, 'users': 0}


def resolve_user_role(context: Context, source: models.Organization):
    if source.owner == context.username:
        return OrganisationUserRole.Owner.value
    elif source.SamlGroupName in context.groups:
        return OrganisationUserRole.Admin.value
    else:
        with context.engine.scoped_session() as session:
            if Organization.find_organization_membership(
                session=session, uri=source.organizationUri, groups=context.groups
            ):
                return OrganisationUserRole.Invited.value
    return OrganisationUserRole.NoPermission.value


def archive_organization(context: Context, source, organizationUri: str = None):
    with context.engine.scoped_session() as session:
        return Organization.archive_organization(
            session=session,
            uri=organizationUri,
        )


def invite_group(context: Context, source, input):
    with context.engine.scoped_session() as session:
        organization, organization_group = Organization.invite_group(
            session=session,
            uri=input['organizationUri'],
            data=input,
        )
        return organization


def remove_group(context: Context, source, organizationUri=None, groupUri=None):
    with context.engine.scoped_session() as session:
        organization = Organization.remove_group(
            session=session,
            uri=organizationUri,
            group=groupUri
        )
        return organization


def list_organization_invited_groups(
    context: Context, source, organizationUri=None, filter=None
):
    if filter is None:
        filter = {}
    with context.engine.scoped_session() as session:
        return Organization.paginated_organization_invited_groups(
            session=session,
            uri=organizationUri,
            data=filter,
        )


def list_organization_groups(
    context: Context, source, organizationUri=None, filter=None
):
    if filter is None:
        filter = {}
    with context.engine.scoped_session() as session:
        return Organization.paginated_organization_groups(
            session=session,
            uri=organizationUri,
            data=filter,
        )


def resolve_organization_by_env(context, source, **kwargs):
    """
    Resolves the organization for environmental resource.
    """
    if not source:
        return None
    with context.engine.scoped_session() as session:
        env: Environment = session.query(Environment).get(
            source.environmentUri
        )
        return session.query(models.Organization).get(env.organizationUri)
