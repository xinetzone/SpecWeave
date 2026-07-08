This example demonstrates a straightforward way to use the mobile-use SDK without builders or advanced configuration. It performs a real-world automation task.

This example is available on GitHub: [simple\_photo\_organizer.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/simple_photo_organizer.py)

## What This Example Does

## Key Concepts

## Simple Agent Creation

Uses default configuration with minimal setup

## Structured Output

Returns typed Pydantic model for type-safe results

## Direct run\_task

No builders needed for simple tasks

## Error Handling

Proper try/except/finally pattern

## Complete Code

```python
import asyncio
from datetime import date, timedelta
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk import Agent

class PhotosResult(BaseModel):
    """Structured result from photo search."""

    found_photos: int = Field(..., description="Number of photos found")
    date_range: str = Field(..., description="Date range of photos found")
    album_created: bool = Field(..., description="Whether an album was created")
    album_name: str = Field(..., description="Name of the created album")
    photos_moved: int = Field(0, description="Number of photos moved to the album")

async def main() -> None:
    # Create a simple agent with default configuration
    agent = Agent()

    try:
        # Initialize agent (finds a device, starts required servers)
        await agent.init()

        # Calculate yesterday's date for the example
        yesterday = date.today() - timedelta(days=1)
        formatted_date = yesterday.strftime("%B %d")  # e.g. "August 22"

        print(f"Looking for photos from {formatted_date}...")

        # First task: search for photos and organize them, with typed output
        result = await agent.run_task(
            goal=(
                f"Open the Photos/Gallery app. Find photos taken on {formatted_date}. "
                f"Create a new album named '{formatted_date} Memories' and "
                f"move those photos into it. Count how many photos were moved."
            ),
            output=PhotosResult,
            name="organize_photos",
        )

        # Handle and display the result
        if result:
            print("\n=== Photo Organization Complete ===")
            print(f"Found: {result.found_photos} photos from {result.date_range}")

            if result.album_created:
                print(f"Created album: '{result.album_name}'")
                print(f"Moved {result.photos_moved} photos to the album")
            else:
                print("No album was created")
        else:
            print("Failed to organize photos")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always clean up resources
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## Code Breakdown

### 1\. Define Output Structure

```python
class PhotosResult(BaseModel):
    found_photos: int = Field(..., description="Number of photos found")
    date_range: str = Field(..., description="Date range of photos found")
    album_created: bool = Field(..., description="Whether an album was created")
    album_name: str = Field(..., description="Name of the created album")
    photos_moved: int = Field(0, description="Number of photos moved to the album")
```

Use detailed field descriptions to help the LLM extract accurate data.

### 2\. Create Agent with Default Config

```python
agent = Agent()
```

No configuration needed for simple use cases. The agent will use default settings.

### 3\. Initialize the Agent

```python
await agent.init()
```

This connects to the first available device and starts required servers.

Note that `init()` is now an async method and must be awaited.

### 4\. Run Task with Structured Output

```python
result = await agent.run_task(
    goal="...",  # Natural language goal
    output=PhotosResult,  # Pydantic model for output
    name="organize_photos"  # Optional task name
)
```

The result is automatically validated and typed as `PhotosResult | None`.

### 5\. Always Clean Up

```python
finally:
    await agent.clean()
```

Always call `await agent.clean()` in a `finally` block to ensure resources are released. Note that `clean()` is now an async method.

## Running the Example

## Expected Output

```text
Looking for photos from October 08...

=== Photo Organization Complete ===
Found: 12 photos from October 08
Created album: 'October 08 Memories'
Moved 12 photos to the album
```

## Customization Ideas

Change date range

```python
# Last week
week_ago = date.today() - timedelta(days=7)

# Specific date
specific_date = date(2024, 10, 1)
```

Filter by photo type

```python
goal = (
    f"Find all selfie photos from {formatted_date} and "
    f"create an album called 'Selfies - {formatted_date}'"
)
```

Multiple albums

```python
# Run multiple tasks in sequence
for i in range(7):
    day = date.today() - timedelta(days=i)
    await agent.run_task(
        goal=f"Organize photos from {day.strftime('%B %d')}",
        output=PhotosResult
    )
```

## What’s Next

## App Lock - Messaging Example

Learn how to restrict execution to a specific app

## Smart Notification Assistant

More advanced example with multiple profiles

## SDK Reference

Explore the complete SDK
