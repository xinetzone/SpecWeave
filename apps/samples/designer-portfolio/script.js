/**
 * 设计师作品集网站交互脚本
 * 模块：导航控制、平滑滚动、滚动动画、作品交互、固定返回按钮、图片懒加载
 */

(function () {
  "use strict";

  /* ========================================
     工具函数
     ======================================== */

  /**
   * 安全执行函数，捕获并报告错误
   * @param {Function} fn - 要执行的函数
   * @param {string} context - 错误上下文描述
   */
  function safeRun(fn, context) {
    try {
      return fn();
    } catch (error) {
      console.error(`[${context}]`, error);
    }
  }

  /**
   * 缓动函数：easeInOutCubic
   * @param {number} t - 0 到 1 的时间进度
   * @returns {number}
   */
  function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  /* ========================================
     模块 1：导航控制
     ======================================== */

  function initNavigation() {
    var header = document.getElementById("header");
    var menuToggle = document.getElementById("menuToggle");
    var mobileNav = document.getElementById("mobileNav");
    var mobileLinks = document.querySelectorAll(".site-header__mobile-link");
    var desktopLinks = document.querySelectorAll(".site-header__link");
    var lastScrollY = window.scrollY || window.pageYOffset;

    if (!header) return;

    /**
     * 更新导航栏滚动状态：超过 100px 时添加毛玻璃背景
     */
    function updateHeaderState() {
      var currentScrollY = window.scrollY || window.pageYOffset;

      if (currentScrollY > 100) {
        header.classList.add("is-scrolled");
      } else {
        header.classList.remove("is-scrolled");
      }

      lastScrollY = currentScrollY;
    }

    /**
     * 切换移动端菜单
     */
    function toggleMobileMenu() {
      var isOpen = mobileNav.classList.toggle("is-open");
      menuToggle.classList.toggle("is-active", isOpen);
      menuToggle.setAttribute("aria-expanded", String(isOpen));
      document.body.style.overflow = isOpen ? "hidden" : "";
    }

    /**
     * 关闭移动端菜单
     */
    function closeMobileMenu() {
      mobileNav.classList.remove("is-open");
      menuToggle.classList.remove("is-active");
      menuToggle.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    }

    // 监听滚动
    window.addEventListener(
      "scroll",
      function () {
        window.requestAnimationFrame(updateHeaderState);
      },
      { passive: true }
    );

    // 初始化状态
    updateHeaderState();

    // 汉堡按钮事件
    if (menuToggle && mobileNav) {
      menuToggle.addEventListener("click", toggleMobileMenu);

      mobileLinks.forEach(function (link) {
        link.addEventListener("click", function () {
          closeMobileMenu();
        });
      });

      // 点击菜单外部关闭
      mobileNav.addEventListener("click", function (event) {
        if (event.target === mobileNav) {
          closeMobileMenu();
        }
      });

      // ESC 键关闭
      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && mobileNav.classList.contains("is-open")) {
          closeMobileMenu();
        }
      });
    }

    return {
      desktopLinks: desktopLinks,
      mobileLinks: mobileLinks,
    };
  }

  /* ========================================
     模块 2：平滑滚动与板块激活
     ======================================== */

  function initSmoothScroll(navLinks) {
    var sections = ["hero", "works", "experience", "contact"];
    var duration = 800; // 滚动时长 800ms

    /**
     * 对指定目标执行平滑滚动
     * @param {string|HTMLElement} target - 目标选择器或元素
     * @param {Function} [onComplete] - 滚动完成回调
     */
    function smoothScrollTo(target, onComplete) {
      var targetElement = typeof target === "string" ? document.querySelector(target) : target;
      if (!targetElement) return;

      var headerHeight = document.getElementById("header")?.offsetHeight || 72;
      var start = window.scrollY || window.pageYOffset;
      var end = targetElement.getBoundingClientRect().top + start - headerHeight;
      var distance = end - start;
      var startTime = null;

      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var elapsed = timestamp - startTime;
        var progress = Math.min(elapsed / duration, 1);
        var easedProgress = easeInOutCubic(progress);

        window.scrollTo(0, start + distance * easedProgress);

        if (progress < 1) {
          window.requestAnimationFrame(step);
        } else if (typeof onComplete === "function") {
          onComplete();
        }
      }

      window.requestAnimationFrame(step);
    }

    /**
     * 判断当前是否在作品详情页
     * @returns {boolean}
     */
    function isProjectDetailPage() {
      var path = window.location.pathname;
      return path.indexOf("/projects/project-") !== -1 || path.indexOf("\\projects\\project-") !== -1;
    }

    /**
     * 高亮当前可见板块对应的导航项
     * 在作品详情页时，默认高亮"作品展示"
     */
    function updateActiveSection() {
      var activeId = "";

      if (isProjectDetailPage()) {
        activeId = "works";
      } else {
        var headerHeight = document.getElementById("header")?.offsetHeight || 72;
        var scrollPosition = (window.scrollY || window.pageYOffset) + headerHeight + 80;

        sections.forEach(function (id) {
          var section = document.getElementById(id);
          if (!section) return;

          var offsetTop = section.offsetTop;
          var offsetBottom = offsetTop + section.offsetHeight;

          if (scrollPosition >= offsetTop && scrollPosition < offsetBottom) {
            activeId = id;
          }
        });

        // 未命中时默认首页
        if (!activeId && (window.scrollY || window.pageYOffset) < 200) {
          activeId = "hero";
        }
      }

      navLinks.forEach(function (link) {
        var target = link.getAttribute("data-target");
        link.classList.toggle("is-active", target === activeId);
      });
    }

    // 为所有导航链接绑定平滑滚动
    navLinks.forEach(function (link) {
      link.addEventListener("click", function (event) {
        var target = link.getAttribute("href");
        if (target && target.startsWith("#")) {
          event.preventDefault();
          smoothScrollTo(target);
        }
      });
    });

    // 监听滚动以更新激活状态
    window.addEventListener(
      "scroll",
      function () {
        window.requestAnimationFrame(updateActiveSection);
      },
      { passive: true }
    );

    // 初始化激活状态
    updateActiveSection();

    return { smoothScrollTo: smoothScrollTo };
  }

  /* ========================================
     模块 3：滚动动画（GSAP + ScrollTrigger）
     ======================================== */

  function initScrollAnimations() {
    if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
      console.warn("GSAP 或 ScrollTrigger 未加载，跳过滚动动画。");
      return;
    }

    gsap.registerPlugin(ScrollTrigger);

    var animatedElements = document.querySelectorAll(
      ".works__header, .work-card, .experience__header, .timeline, .contact__container"
    );

    animatedElements.forEach(function (element) {
      gsap.fromTo(
        element,
        { opacity: 0, y: 32 },
        {
          opacity: 1,
          y: 0,
          duration: 0.5,
          ease: "power2.out",
          scrollTrigger: {
            trigger: element,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        }
      );
    });

    // Hero 区域淡入
    gsap.fromTo(
      ".hero__content",
      { opacity: 0, y: 24 },
      { opacity: 1, y: 0, duration: 0.8, ease: "power2.out", delay: 0.2 }
    );

  }

  /* ========================================
     模块 4：作品交互
     ======================================== */

  function initWorksInteraction() {
    var cards = document.querySelectorAll(".work-card");

    cards.forEach(function (card) {
      card.addEventListener("click", function (event) {
        var link = card.querySelector(".work-card__link");
        if (link && link.href) {
          // 允许默认跳转，此处仅做可扩展的事件处理
          try {
            var projectId = card.getAttribute("data-project");
            console.log("打开作品详情：project-" + projectId);
          } catch (error) {
            console.error("作品点击事件处理失败", error);
          }
        }
      });
    });
  }

  /* ========================================
     模块 5：固定返回按钮
     ======================================== */

  function initBackButton() {
    var backButton = document.getElementById("backButton");
    if (!backButton) return;

    var showThreshold = 200;

    function toggleBackButton() {
      var scrollY = window.scrollY || window.pageYOffset;
      if (scrollY > showThreshold) {
        backButton.classList.add("is-visible");
      } else {
        backButton.classList.remove("is-visible");
      }
    }

    window.addEventListener(
      "scroll",
      function () {
        window.requestAnimationFrame(toggleBackButton);
      },
      { passive: true }
    );

    // 初始化状态
    toggleBackButton();
  }

  /* ========================================
     模块 6：图片懒加载增强
     ======================================== */

  function initLazyLoading() {
    var images = document.querySelectorAll("img[loading='lazy']");

    if ("loading" in HTMLImageElement.prototype) {
      // 浏览器原生支持 lazy loading
      images.forEach(function (img) {
        img.setAttribute("loading", "lazy");
      });
      return;
    }

    // 降级方案：Intersection Observer
    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              var img = entry.target;
              var src = img.getAttribute("data-src");
              if (src) {
                img.src = src;
                img.removeAttribute("data-src");
              }
              observer.unobserve(img);
            }
          });
        },
        { rootMargin: "100px" }
      );

      images.forEach(function (img) {
        var currentSrc = img.getAttribute("src");
        if (currentSrc) {
          img.setAttribute("data-src", currentSrc);
          img.removeAttribute("src");
          observer.observe(img);
        }
      });
    }
  }

  /* ========================================
     初始化入口
     ======================================== */

  function init() {
    safeRun(function () {
      var nav = initNavigation();
      var allNavLinks = Array.from(nav.desktopLinks).concat(Array.from(nav.mobileLinks));
      initSmoothScroll(allNavLinks);
    }, "导航与平滑滚动初始化");

    safeRun(function () {
      initScrollAnimations();
    }, "滚动动画初始化");

    safeRun(function () {
      initWorksInteraction();
    }, "作品交互初始化");

    safeRun(function () {
      initBackButton();
    }, "固定返回按钮初始化");

    safeRun(function () {
      initLazyLoading();
    }, "懒加载初始化");
  }

  // DOM 就绪后执行
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
