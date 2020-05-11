Feature: The supplier catalog service back-end
    As a Supplier Manager
    I need a RESTful catalog service
    So that I can keep track of all my suppliers

Background:
    Given the following suppliers
        | name | category | preferred |
        | John | home & furnishing | True |
        | Jane | apparel | False |
        | Jack | apparel | False |

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
    
Scenario: Delete a Supplier
    When I visit the "Home Page"
    And I set the "name" to "John"
    And I set the "category" to "home & furnishing"
    And I select "True" in the "Preferred" dropdown
    And I press the "search" button
    Then I should see "John" in the "name" field
    And I should see "home & furnishing" in the "category" field
    When I copy the "Id" field
    And I press the "clear" button
    And I paste the "Id" field
    And I press the "Delete" button
    And I paste the "Id" field
    And I press the "search" button
    Then I should not see "John" in the results

Scenario: Retrieve a Supplier
    When I visit the "Home Page"
    And I set the "name" to "John"
    And I set the "category" to "home & furnishing"
    And I select "True" in the "Preferred" dropdown
    And I press the "search" button
    Then I should see "John" in the "name" field
    And I should see "home & furnishing" in the "category" field
    When I copy the "Id" field
    And I press the "clear" button
    And I paste the "Id" field
    And I press the "retrieve" button
    Then I should see "John" in the "name" field

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

Scenario: Update a Supplier
    When I visit the "Home Page"
    And I set the "name" to "John"
    And I press the "Search" button
    Then I should see "John" in the "name" field
    And I should see "home & furnishing" in the "Category" field
    When I change "name" to "Fred"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "Fred" in the "name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "Fred" in the results
    Then I should not see "John" in the results

Scenario: Mark a Supplier as Preferred
    When I visit the "Home Page"
    And I set the "name" to "Jane"
    And I press the "Search" button
    Then I should see "Jane" in the "name" field
    And I should see "apparel" in the "Category" field
    And I should see "False" in the "Preferred" dropdown
    When I copy the "Id" field
    And I press the "clear" button
    And I paste the "Id" field
    And I press the "mark-preferred" button
    Then I should see the message "Success"
    When I press the "clear" button
    And I set the "name" to "Jane"
    And I set the "Category" to "apparel"
    And I press the "Search" button
    Then I should see "Jane" in the results
    And I should see "apparel" in the results
    And I should see "true" in the results
    And I should not see "false" in the results
    


    
    





