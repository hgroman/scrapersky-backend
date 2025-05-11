# Example File: tests/workflows/test_{workflow_name}_workflow.py
import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID

from src.models.{source_table_name} import {SourceTableTitleCase}
from src.models.{source_table_name} import {WorkflowNameTitleCase}CurationStatus, {WorkflowNameTitleCase}ProcessingStatus

@pytest.mark.asyncio
async def test_{workflow_name}_api_status_update_and_queueing(
    async_client: AsyncClient,
    db_session
):
    async def create_test_{source_table_name}(session, **kwargs):
        from src.models.{source_table_name} import {SourceTableTitleCase}
        from uuid import uuid4
        default_values = {{
            "id": uuid4(),
        }}
        default_values.update(kwargs)
        instance = {SourceTableTitleCase}(**default_values)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    test_record = await create_test_{source_table_name}(
        db_session,
        {workflow_name}_curation_status={WorkflowNameTitleCase}CurationStatus.New
    )
    test_id = test_record.id

    response = await async_client.put(
        f"/api/v3/{source_table_plural_name}/status",
        json={{"ids": [str(test_id)], "status": {WorkflowNameTitleCase}CurationStatus.Queued.value}}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"].startswith("Updated 1")
    assert str(test_id) in response_data["updated_ids"]

    await db_session.refresh(test_record)
    assert test_record.{workflow_name}_curation_status == {WorkflowNameTitleCase}CurationStatus.Queued
    assert test_record.{workflow_name}_processing_status == {WorkflowNameTitleCase}ProcessingStatus.Queued
    assert test_record.{workflow_name}_processing_error is None

@pytest.mark.asyncio
async def test_{workflow_name}_service_processing_success(
    db_session
):
    from src.services.{workflow_name}_service import process_single_{source_table_name}_for_{workflow_name}

    async def create_test_{source_table_name}(session, **kwargs):
        from src.models.{source_table_name} import {SourceTableTitleCase}
        from uuid import uuid4
        default_values = {{"id": uuid4()}}
        default_values.update(kwargs)
        instance = {SourceTableTitleCase}(**default_values)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    test_record = await create_test_{source_table_name}(
        db_session,
        {workflow_name}_curation_status={WorkflowNameTitleCase}CurationStatus.Queued,
        {workflow_name}_processing_status={WorkflowNameTitleCase}ProcessingStatus.Processing,
    )
    test_id = test_record.id

    await process_single_{source_table_name}_for_{workflow_name}(db_session, test_id)

    await db_session.refresh(test_record)
    assert test_record.{workflow_name}_processing_status == {WorkflowNameTitleCase}ProcessingStatus.Completed
    assert test_record.{workflow_name}_processing_error is None

# @pytest.mark.asyncio
# async def test_{workflow_name}_api_invalid_input(async_client: AsyncClient, db_session):
#   pass

# @pytest.mark.asyncio
# async def test_{workflow_name}_service_processing_error(db_session, mocker):
#   pass

# @pytest.mark.asyncio
# async def test_{workflow_name}_scheduler_finds_and_processes(db_session, mocker):
#   pass
