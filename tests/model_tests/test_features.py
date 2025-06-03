from models.feature import Feature

with open("assets/feature.json", "r") as file:
    json_data = file.read()

def test_feature_creation():
    """Test creating a Feature from JSON data."""
    # Load the JSON data and create a Feature instance
    feature = Feature.model_validate_json(json_data)

    # Check if the feature was created successfully
    assert isinstance(feature, Feature)
    assert feature.id is not None
    assert feature.name == "Feature"
    assert feature.description == "A feature that can be toggled on or off."
    assert feature.id.version == 4 

# A pydantic should error if JSON does not contain the name and description fields
def test_feature_creation_invalid_json():
    """Test creating a Feature with invalid JSON data."""
    invalid_json = '{"id": "12345"}'  # Missing name and description
    try:
        Feature.model_validate_json(invalid_json)
        assert False, "Expected validation error but none was raised."
    except ValueError as e:
        assert "name" in str(e) and "description" in str(e)