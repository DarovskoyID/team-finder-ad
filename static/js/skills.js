(function () {
  document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("skills-container");
    const addButton = document.getElementById("add-skill-btn");
    if (!container || !addButton) return;

    const wrapper = document.getElementById("skill-input-wrapper");
    const input = document.getElementById("skill-input");
    const suggestions = document.getElementById("skill-suggestions");
    let timer;
    let searchController;
    let busy = false;
    input.maxLength = Number(container.dataset.maxLength);

    function showError(error) {
      window.toast(error.message, { type: "error" });
    }

    function hideInput() {
      clearTimeout(timer);
      if (searchController) searchController.abort();
      wrapper.classList.add("hidden");
      suggestions.classList.add("hidden");
      addButton.classList.remove("hidden");
    }

    function appendChip(id, name) {
      if (container.querySelector(`[data-id="${id}"]`)) return;
      const chip = document.createElement("span");
      chip.className = "skill-chip";
      chip.dataset.id = id;
      chip.append(document.createTextNode(name + " "));
      const button = document.createElement("button");
      button.type = "button";
      button.className = "remove-skill-btn";
      button.setAttribute("aria-label", "Удалить навык");
      button.textContent = "×";
      chip.append(button);
      container.insertBefore(chip, addButton);
      container.querySelector(".skill-empty")?.remove();
    }

    async function addSkill(payload) {
      if (busy) return;
      busy = true;
      try {
        const skill = await window.postJSON(container.dataset.addUrl, payload);
        appendChip(skill.skill_id, skill.name);
        hideInput();
      } catch (error) {
        showError(error);
      } finally {
        busy = false;
      }
    }

    function addSuggestion(name, id) {
      const item = document.createElement("li");
      item.textContent = id ? name : `Создать «${name}»`;
      item.dataset.name = name;
      if (id) item.dataset.id = id;
      item.className = id ? "suggestion-item" : "create-new";
      suggestions.append(item);
    }

    addButton.addEventListener("click", () => {
      addButton.classList.add("hidden");
      wrapper.classList.remove("hidden");
      suggestions.replaceChildren();
      suggestions.classList.add("hidden");
      input.value = "";
      input.focus();
    });

    input.addEventListener("input", () => {
      clearTimeout(timer);
      if (searchController) searchController.abort();
      const query = input.value.trim();
      suggestions.replaceChildren();
      suggestions.classList.add("hidden");
      if (!query) return;
      timer = setTimeout(async () => {
        searchController = new AbortController();
        try {
          const url = container.dataset.searchUrl + "?q=" + encodeURIComponent(query);
          const response = await fetch(url, {
            signal: searchController.signal,
          });
          if (!response.ok) throw new Error("Не удалось найти навыки");
          const skills = await response.json();
          if (input.value.trim() !== query) return;
          suggestions.replaceChildren();
          skills.forEach(skill => addSuggestion(skill.name, skill.id));
          if (!skills.some(skill => skill.name === query)) {
            addSuggestion(query);
          }
          suggestions.classList.remove("hidden");
        } catch (error) {
          if (error.name !== "AbortError") showError(error);
        }
      }, 200);
    });

    suggestions.addEventListener("mousedown", event => {
      const item = event.target.closest("li");
      if (!item) return;
      event.preventDefault();
      addSkill(item.dataset.id
        ? { skill_id: item.dataset.id }
        : { name: item.dataset.name });
    });

    input.addEventListener("keydown", event => {
      if (event.key === "Escape") hideInput();
      if (event.key !== "Enter") return;
      event.preventDefault();
      const name = input.value.trim();
      if (!name) return;
      const match = Array.from(suggestions.children).find(
        item => item.dataset.id && item.dataset.name === name,
      );
      addSkill(match ? { skill_id: match.dataset.id } : { name });
    });

    input.addEventListener("blur", () => {
      if (!busy) hideInput();
    });

    container.addEventListener("click", async event => {
      const button = event.target.closest(".remove-skill-btn");
      if (!button || button.disabled) return;
      const chip = button.closest(".skill-chip");
      button.disabled = true;
      try {
        await window.postJSON(container.dataset.removeUrl.replace("/0/", `/${chip.dataset.id}/`));
        chip.remove();
        if (!container.querySelector(".skill-chip")) {
          const empty = document.createElement("span");
          empty.className = "skill-empty";
          empty.textContent = "Навыки не указаны";
          container.insertBefore(empty, addButton);
        }
      } catch (error) {
        showError(error);
        button.disabled = false;
      }
    });
  });
})();
