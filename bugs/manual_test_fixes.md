# Bug and Feature Request Analysis

This document outlines the design and execution plan for the bugs and missing features identified during manual testing.

---

## 1. Unique Space Names

**Analysis:** The system currently allows the creation of spaces with duplicate names within the same site, which can lead to confusion and data integrity issues. The space name should be unique per site.

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **Database Layer:** Apply a unique composite constraint on the `spaces` table for the `(site_id, name)` columns using an Alembic migration. This will provide the ultimate data integrity guarantee.
    2.  **Service Layer:** In the `SpaceService.create_space` method, before attempting to create the space, add a check to see if a space with the same name already exists for the given `site_id`.
    3.  **API Layer:** If the check fails, raise an `HTTPException` with a `409 Conflict` status code and a clear error message in Chinese (e.g., "此場地已存在同名車位").

*   **Frontend (Next.js):**
    1.  **Error Handling:** In the "Create Space" form, update the API call logic to catch the `409 Conflict` error.
    2.  **User Feedback:** When this error is caught, display a user-friendly error message next to the name input field, informing the user that the name is already taken.

---

## 2. Batch Space Creation and Sequential Naming

**Analysis:** There is currently no batch space creation workflow. The user wants to add a feature to create multiple spaces at once with sequential naming (e.g., A-01, A-02, A-03).

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **New API Endpoint:** Create a new API endpoint, e.g., `POST /api/v1/spaces/batch`, which accepts a batch configuration.
    2.  **New Pydantic Schema:** Define a schema `SpaceBatchCreateRequest` that accepts:
        *   `site_id: int`
        *   `prefix: str`
        *   `count: int` (number of spaces to create)
        *   `start_number: int = 1` (starting sequential number, e.g., for 'A-01')
        *   `tags: Optional[List[int]] = None` (list of tag IDs to apply to all spaces in the batch)
        *   `custom_price: Optional[float] = None` (optional custom price for all spaces in the batch)
    3.  **Service Layer:**
        *   Implement a new method `SpaceService.batch_create_spaces(db: Session, batch_data: SpaceBatchCreateRequest, current_user: AdminUser) -> List[Space]`.
        *   This method will first validate `site_id` exists and is accessible.
        *   It will generate space names using the provided `prefix` and sequential numbers, padding with leading zeros (e.g., `f"{prefix}-{i:02d}"`).
        *   **Pre-check for Duplicates:** Before attempting any creation, query the database to check if *any* of the generated names already exist within the specified `site_id`. If duplicates are found, raise an `HTTPException` with `409 Conflict` and a list of conflicting names.
        *   **Transaction:** Wrap the creation of all spaces in a single database transaction to ensure atomicity (all or nothing).
        *   For each new space, call the existing `SpaceService.create_space` logic (or a modified internal version) to reuse validation and business rules.
        *   **Audit Logging:** Log a single 'BATCH_CREATE_SPACES' action in `system_logs`, detailing the `site_id`, `prefix`, `count`, and the `id`s of the newly created spaces.

*   **Frontend (Next.js):**
    1.  **UI Entry Point:** Add a "Batch Create Spaces" button on the Space Management page (e.g., near the existing "Create Space" button).
    2.  **Modal Form:** Clicking the button will open a modal form with the following inputs:
        *   Site (Dropdown/Select)
        *   Prefix (Text input)
        *   Number of Spaces (Number input)
        *   Starting Number (Number input, default to 1)
        *   Tags (Multi-select dropdown, fetching available tags)
        *   Custom Price (Optional number input)
    3.  **API Integration:** On form submission, send a `POST` request to `/api/v1/spaces/batch` with the form data.
    4.  **User Feedback:**
        *   Display a loading indicator during the API call.
        *   On success, show a toast notification (e.g., "Successfully created X spaces") and close the modal. Refresh the space list.
        *   On error, display a clear, user-friendly error message in Chinese within the modal (e.g., if duplicate names were found, list them).

---

## 3. Display Tag Colors in Space List

**Analysis:** The space list page shows tags as plain text. The system was designed to have color-coded tags for better visual scanning, but this is not implemented on the list page. The `tags` table has a `color` column.

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **Verify API Response:** Ensure the `GET /api/v1/spaces` endpoint returns the full tag object (including `id`, `name`, and `color`) for each space, not just the tag name. The Pydantic schema for the space response model should be configured for this.

*   **Frontend (Next.js):**
    1.  **Locate Component:** Identify the component responsible for rendering the spaces table (likely in `src/app/(dashboard)/spaces/components/space-table.tsx`).
    2.  **Update Tag Rendering:** In the table cell that renders tags, map over the `space.tags` array.
    3.  **Apply Color:** For each tag, use a `Badge` component (from shadcn/ui). Apply the tag's color using an inline style: `style={{ backgroundColor: tag.color }}`. Ensure the text color has sufficient contrast (e.g., by setting it to black or white based on the background color's brightness).

---

## 4. Workflow to Add/Remove Tags from a Space

**Analysis:** A core piece of functionality is missing: the ability to change the tags associated with an existing space. This should be possible from the space detail page.

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **New API Endpoint:** Create `PUT /api/v1/spaces/{space_id}/tags`.
    2.  **Pydantic Schema:** Define `SpaceTagsUpdate` schema with a single field: `tag_ids: List[int]`.
    3.  **Service Logic:**
        *   Implement `SpaceService.update_space_tags`.
        *   This service will fetch the space by `space_id`.
        *   It will replace the existing list of tags on the space with the new list provided. Since tags are a PG array, this is a simple update to the column.
        *   Log the change (old tags vs. new tags) in the `system_logs` table via the `AuditLogger`.

*   **Frontend (Next.js):**
    1.  **Location:** On the space detail page (`/spaces/[id]`).
    2.  **UI Component:** Add a section for "Tags". Use a multi-select combobox component (e.g., from shadcn/ui) that allows searching and selecting from all available tags.
    3.  **State Management:** The component should be populated with the space's current tags.
    4.  **Interaction:** When the user modifies the tags and clicks a "Save" or "Update" button, call the new `PUT /api/v1/spaces/{space_id}/tags` endpoint with the updated list of tag IDs.
    5.  **Feedback:** Show a confirmation toast on success.

---

## 5. Workflow to Manually Edit a Space's Price

**Analysis:** The pricing model specifies that an admin can override the site or tag-based price with a custom price for a specific space. The UI for this is missing.

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **Verify Model/Schema:** The `Space` model should have a `custom_price: Optional[Decimal]` field. Ensure this is reflected in the Pydantic schemas.
    2.  **New API Endpoint:** Create `PUT /api/v1/spaces/{space_id}/price`.
    3.  **Pydantic Schema:** Define a schema `SpacePriceUpdate` that accepts `{ custom_price: Optional[float] }`.
    4.  **Service Logic:**
        *   Implement `SpaceService.update_space_price`.
        *   This service updates the `custom_price` field for the specified space. Setting it to `null` should revert the space to using the tag or site-based price.
        *   Log the price change in `system_logs`.

*   **Frontend (Next.js):**
    1.  **Location:** On the space detail page (`/spaces/[id]`).
    2.  **UI Component:** In an "Edit Space" form or a dedicated "Pricing" card, add an input field for "Custom Price".
    3.  **Display Logic:**
        *   Clearly label the input.
        *   Display the *effective* current price and indicate its source (e.g., "Site Default: NT$3600", "Tag Price: NT$3800", or "Custom Price: NT$3750").
        *   The input should show the current `custom_price` if set.
    4.  **Interaction:** When an admin enters a value and saves, call the `PUT /api/v1/spaces/{space_id}/price` endpoint. A button to "Clear Override" could set the price back to `null`.
    5.  **Feedback:** Show a confirmation toast and update the displayed effective price.
