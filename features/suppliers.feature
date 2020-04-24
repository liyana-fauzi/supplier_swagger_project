Feature: The supplier catalog service back-end
    As a Supplier Manager
    I need a RESTful catalog service
    So that I can keep track of all my suppliers

Background:
    Given the following suppliers
        | name | category | preferred |
        | John | home & furnishing | True |
        | Jane | apparel | False |
        | Jack | apparel | True |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Supplier Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Supplier
    When I visit the "Home Page"
    And I set the "name" to "David"
    And I set the "category" to "health & beauty"
    And I select "False" in the "Preferred" dropdown
    And I press the "create" button
    Then I should see the message "Success"
    
Scenario: List all suppliers
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "John" in the results
    And I should see "Jane" in the results
    And I should not see "Liyana" in the results

Scenario: Query Supplier based on Category
    When I visit the "Home Page"
    And I set the "Category" to "apparel"
    And I press the "Search" button
    Then I should see "Jane" in the results
    And I should not see "John" in the results
    And I should not see "Liyana" in the results    

