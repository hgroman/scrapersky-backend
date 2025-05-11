// Example File: static/js/page-curation-tab.js (using page_curation as example for placeholders)
$(document).ready(function () {
  const workflowName = "{workflow_name}";
  const workflowNameCamelCase = "{workflowNameCamelCase}";
  const workflowNameTitleCase = "{WorkflowNameTitleCase}";
  const sourceTablePlural = "{source_table_plural_name}";

  const curationStatusEnum = {
    New: "New",
    Queued: "Queued",
    Processing: "Processing",
    Complete: "Complete",
    Error: "Error",
    Skipped: "Skipped",
  };

  const tableBody = $(`#${workflowNameCamelCase}TableBody`);
  const selectAllCheckbox = $(`#selectAll${workflowNameTitleCase}Checkbox`);
  const itemCheckboxClass = `${workflowNameCamelCase}-item-checkbox`;

  const queueSelectedBtn = $(`#update-${sourceTablePlural}-status-queued`);
  const markSkippedBtn = $(`#update-${sourceTablePlural}-status-skipped`);

  function loadData() {
    $.ajax({
      url: `/api/v3/${sourceTablePlural}/list`,
      type: "GET",
      success: function (response) {
        populateTable(response.items || []);
        selectAllCheckbox.prop("checked", false);
      },
      error: function (error) {
        showNotification(
          "Error",
          `Failed to load ${sourceTablePlural} data. Check console for details.`
        );
        console.error("Load error:", error);
      },
    });
  }

  function populateTable(items) {
    tableBody.empty();
    if (!items || items.length === 0) {
      tableBody.append(
        `<tr><td colspan="4">No items found for ${workflowName} workflow.</td></tr>`
      );
      return;
    }
    items.forEach((item) => {
      const curationStatus =
        item[`${workflow_name}_curation_status`] || curationStatusEnum.New;
      const processingStatus = item[`${workflow_name}_processing_status`] || "N/A";
      tableBody.append(`
        <tr>
            <td><input type="checkbox" class="${itemCheckboxClass}" data-id="${item.id}"></td>
            <td>${item.id}</td>
            <td>${curationStatus}</td>
            <td>${processingStatus}</td>
        </tr>
      `);
    });
  }

  function getSelectedIds() {
    return $(`.${itemCheckboxClass}:checked`)
      .map(function () {
        return $(this).data("id");
      })
      .get();
  }

  function updateStatus(newCurationStatusValue) {
    const selectedIds = getSelectedIds();
    if (selectedIds.length === 0) {
      showNotification("Warning", "Please select at least one item.");
      return;
    }
    const apiUrl = `/api/v3/${sourceTablePlural}/status`;

    $.ajax({
      url: apiUrl,
      type: "PUT",
      contentType: "application/json",
      data: JSON.stringify({
        ids: selectedIds,
        status: newCurationStatusValue,
      }),
      success: function (response) {
        showNotification("Success", response.message || "Status updated successfully");
        loadData();
      },
      error: function (error) {
        const errorMsg =
          error.responseJSON?.detail ||
          `Failed to update status to ${newCurationStatusValue}. Check console.`;
        showNotification("Error", errorMsg);
        console.error("Update error:", error);
      },
    });
  }

  selectAllCheckbox.on("click", function () {
    $(`.${itemCheckboxClass}`).prop("checked", $(this).prop("checked"));
  });

  queueSelectedBtn.on("click", function () {
    updateStatus(curationStatusEnum.Queued);
  });

  markSkippedBtn.on("click", function () {
    updateStatus(curationStatusEnum.Skipped);
  });

  loadData();
});

function showNotification(title, message) {
  console.log(`Notification - ${title}: ${message}`);
  alert(`${title}: ${message}`);
}
