describe('Logging into the system', () => {
  // define variables that we need on multiple occasions
  let uid;   // user id
  let name;  // name of the user (firstName + ' ' + lastName)
  let email; // email of the user

  before(() => {
    // make user 
  // also creates one task wich is used through out the entire test session
    cy.fixture('user.json').then((user) => {
      cy.request({
        method: 'POST',
        url: 'http://localhost:5000/users/create',
        form: true,
        body: user
      }).then((response) => {
        uid = response.body._id.$oid;
        name = `${user.firstName} ${user.lastName}`;
        email = user.email;

        // logs in and creates a task
        cy.visit("http://localhost:3000");
        cy.get("input[name='email']")
        .type(email);
        cy.get("input[type='submit'][value='Login']")
        .click();

        cy.get("h1")
        .should("contain.text", "Your tasks");

        cy.get('[name=title]')
        .type('test task');

        cy.get("input[name='url']")
        .type("testurltest");
        cy.contains("input[type='submit']", "Create new Task")
        
        
        .click();
        cy.get('.container .title-overlay')
        .should('contain.text', 'test task');
      });
    });
  });

  // runs before each tests, logs in and verifies landing page.
  beforeEach(() => {
    cy.visit("http://localhost:3000");
    cy.get("input[name='email']").type(email);
    cy.get("input[type='submit'][value='Login']").click();
  

    cy.get("h1").should("contain.text", "Your tasks");
  
  });
  
  // selects the created task and adds a new todo ite
  it('R8CU1 1.1 & 1.2: adding a todo item to the created task', () => {
    cy.get('.container')
      .contains('.title-overlay', 'test task')

      .parent('a')
      .click();

    cy.get("input[placeholder='Add a new todo item']")
    .type("test todo item");
    cy.get("input[type='submit'][value='Add']")
    .click();

    cy.contains("test todo item")
    .should('contain.text', 'test todo item');
  });
    //  Selects the task and then clears any descirption of the default todo item.'
  //  checks so that the disabled flag is there. Had to use force: true since item was blocked due to flimsy html structure
  it('R8UC1 2.b: add button remains disabled if description is empty', () => {
    cy.get('.container')
      .contains('.title-overlay', 'test task')
      .parent('a')
      .click();

    cy.get("input[placeholder='Add a new todo item']")
    .clear({ force: true });

    cy.get("input[type='submit'][value='Add']")
    
    .should('be.disabled');
  });


  // enters the task detailed view and presses the done button on a todo item.
  describe('R8UC2 1.1 & 1.2: toggling todo from active to done', () => {
    it('R8UC2 toggles a todo item to done', () => {
      cy.get('.container')
        .contains('.title-overlay', 'test task')
        .parent('a')
        .click();

      cy.get('.todo-list .todo-item')
        .first()

        .find('.checker.unchecked')
        .click();

      cy.get('.todo-list .checker.checked')
      .should('exist');
    });
    //enter the detailed view of the task sets todo item to done the waits and confirms its done with "checked" status
    // then sets todo item to active again and comfirms it is unchecked
    it('R8UC2 2.b: toggle a todo from done to active', () => {
      cy.get('.container')
        .contains('.title-overlay', 'test task')
        .parent('a')
        .click();

      cy.get('.todo-list .todo-item')
        .first()
        .find('.checker')
        .click();
      cy.get('.todo-list .todo-item')
        .first()
        .find('.checker')
        .should('have.class', 'checked')

        .click(); 

      cy.get('.todo-list .todo-item')

        .first()
        .find('.checker')
        .should('have.class', 'unchecked');

    });
    
  });
 // tests deletion of todo item. Enters a tas and presses the "x" button. Confirms that todo item no longer exists
  it('R8UC3: delete todo item.', () => {
    cy.get('.container')
      .contains('.title-overlay', 'test task')
      .parent('a')
      .click();
    cy.contains('.todo-list .todo-item', 'test todo item')
      .find('.remover')

      .click()
      .click();

    cy.get('.todo-list .todo-item')
      .should('not.contain.text', 'test todo item');
  });

  after(function () {
    // clean up by deleting the user from the database
    cy.request({
      method: 'DELETE',
      url: `http://localhost:5000/users/${uid}`
    }).then((response) => {
      cy.log(response.body);
    });
  });
});
